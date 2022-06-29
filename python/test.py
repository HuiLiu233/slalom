import tensorflow as tf

print(tf.__version__)

gpu_device_name = tf.test.gpu_device_name()
print(gpu_device_name)

print(tf.test.is_gpu_available())