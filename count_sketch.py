import tensorflow as tf

_count_sketch_module = tf.load_op_library('./count_sketch.so')
_store = {}

def count_sketch(probs, project_size):
    """ Calculates count-min sketch of a probability distribution.
    Args:
      probs: A `Tensor`
      project_size: output size (`int`)

    Returns:c
      A projected count-min sketch `Tensor` with shape [batch_size, project_size].
    """
    with tf.variable_scope('CountSketch_'+probs.name.replace(':', '_')) as scope:
        input_size = int(probs.get_shape()[1])

        # h, s must be sampled once
        if scope.name in _store:
            print('reuse')
            scope.reuse_variables()
        _store[scope.name] = True
        print(_store)

        h = tf.get_variable('h', [input_size], initializer=tf.random_uniform_initializer(0, project_size), trainable=False)
        s = tf.get_variable('s', [input_size], initializer=tf.random_uniform_initializer(0, 2), trainable=False)

        h = tf.cast(h, 'int32')
        s = tf.cast(tf.floor(s) * 2 - 1, 'int32') # 1 or -1

        sk = _count_sketch_module.count_sketch(probs, h, s, project_size)
        sk.set_shape([probs.get_shape()[0], project_size])
        return sk

@tf.RegisterGradient('CountSketch')
def _count_sketch_grad(op, grad):
    probs, h, s, _ = op.inputs
    input_size = int(probs.get_shape()[1])
    return [_count_sketch_module.count_sketch_grad(grad, h, s, input_size), None, None, None]

def bilinear_pool(x1, x2, output_size):
    """ Computes approximation of outer product with respect to x1, x2.
    For details, see the original paper (https://arxiv.org/abs/1511.06062)

    Args:
      x1: A `Tensor` with shape (batch_size, x1_size).
      x2: A `Tensor` with shape ((batch_size, x2_size).
      output_size: Output projection size. (`int`)

    Returns:
       A Tensor with shape (batch_size, output_size).
    """

    p1 = count_sketch(x1, output_size)
    p2 = count_sketch(x2, output_size)
    pc1 = tf.complex(p1, tf.zeros_like(p1))
    pc2 = tf.complex(p1, tf.zeros_like(p2))

    return tf.batch_ifft(tf.batch_fft(pc1) * tf.batch_fft(pc2))