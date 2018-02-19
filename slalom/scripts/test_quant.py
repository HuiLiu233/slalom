import numpy as np
import tensorflow as tf

from slalom import imagenet
from slalom.utils import Results
from slalom.quant import Conv2DQ, DenseQ
import sys

from keras.applications.vgg16 import VGG16
from keras.applications.inception_v3 import InceptionV3
from keras.applications.imagenet_utils import decode_predictions
from keras.applications.imagenet_utils import preprocess_input
from keras.layers import Conv2D, Dense


def size_to_mb(s, type_bytes=4):
    return (type_bytes * s) / (1.0 * 1024**2)


def quantize(model):
    return model


def print_model_size(model):
    tot_size = 0.0

    for layer in model.layers:
        print(layer.name)
        if layer.__class__ in [Conv2D, Dense]:
            layer_size = np.prod(layer.output.get_shape().as_list()[1:])
            tot_size += layer_size
            print("Layer {}: {:.4f} MB".format(layer.name, size_to_mb(layer_size)))

    print("Total Size: {:.2f} MB".format(size_to_mb(tot_size)))


def test_forward(sess, x, logits, quant=False):

    dataset_images, labels = imagenet.load_validation(
        args.input_dir, args.batch_size, preprocess=preprocess_input)

    num_batches = args.max_num_batches

    coord = tf.train.Coordinator()
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)

    res = Results()

    for i in range(num_batches):
        images, true_labels = sess.run([dataset_images, labels])

        res.start_timer()
        preds = sess.run(logits, feed_dict={x: images})
        print(preds)
        print(true_labels)
        res.end_timer()

        res.record_acc(preds, true_labels)
        res.print_results()
        sys.stdout.flush()

    coord.request_stop()
    coord.join(threads)


def main(_):

    with tf.Session() as sess:

        if args.model_name in ['vgg_16']:
            images = tf.placeholder(dtype=tf.float32, shape=(args.batch_size, 224, 224, 3))
            num_classes = 1000
            model = VGG16(include_top=True, weights='imagenet', input_tensor=images, input_shape=None, pooling=None, classes=num_classes)
        elif args.model_name in ['inception_v3']:
            images = tf.placeholder(dtype=tf.float32, shape=(args.batch_size, 299, 299, 3))
            num_classes = 1000
            model = InceptionV3(include_top=True, weights='imagenet', input_tensor=images, input_shape=None, pooling=None, classes=num_classes)
        else:
            raise AttributeError("unknown model {}".format(args.model_name))

        labels = tf.placeholder(dtype=tf.float32, shape=(args.batch_size, num_classes))
        logits = model.output

        if args.test_name == 'model_size':
            print_model_size(model)
        elif args.test_name == 'forward':
            test_forward(sess, images, logits)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('test_name', type=str,
                        choices=['model_size', 'forward', 'backward'])
    parser.add_argument('model_name', type=str,
                        choices=['vgg_16', 'inception_v3'])

    parser.add_argument('--input_dir', type=str,
                        default='/home/ubuntu/imagenet/',
                        help='Input directory with images.')
    parser.add_argument('--batch_size', type=int, default=8,
                        help='How many images process at one time.')
    parser.add_argument('--max_num_batches', type=int, default=2,
                        help='Max number of batches to evaluate.')
    args = parser.parse_args()
    tf.app.run()
