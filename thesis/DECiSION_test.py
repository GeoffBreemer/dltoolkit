import DECiSION_settings as settings
from thesis_common import read_preprocess_image, read_preprocess_groundtruth,\
    convert_pred_to_img, group_images, model_name_from_arguments

from dltoolkit.nn.segment import UNet_NN

import os, cv2
import numpy as np

import matplotlib.pyplot as plt
# %matplotlib inline

if __name__ == "__main__":
    # Load and preprocess the test and ground truth images (the latter will not be used during inference,
    # only for visualisation)
    if settings.IS_DEVELOPMENT:
        print("--- Pre-processing TRAINING images")
        test_imgs = read_preprocess_image("../data/MSC8002/training/train_imgs.h5", settings.HDF5_KEY)
        test_ground_truths = read_preprocess_groundtruth("../data/MSC8002/training/train_masks.h5", settings.HDF5_KEY)
    else:
        print("--- Pre-processing test images")
        test_imgs = read_preprocess_image(
            os.path.join(settings.TEST_PATH, settings.FLDR_IMAGES + settings.HDF5_EXT), settings.HDF5_KEY)

    # Show an image plus its ground truth to check
    IX = 0
    cv2.imshow("CHECK image", test_imgs[IX])
    print("       Max image intensity: {} - {} - {}".format(np.max(test_imgs[IX]), test_imgs.dtype, test_imgs.shape))
    if settings.IS_DEVELOPMENT:
        cv2.imshow("CHECK ground truth", test_ground_truths[IX])
        print("Max ground truth intensity: {} - {} - {}".format(np.max(test_ground_truths[IX]), test_ground_truths.dtype, test_ground_truths.shape))
    cv2.waitKey(0)

    # Only predict for some images
    PRED_IX = range(0, 9)
    test_imgs = test_imgs[[PRED_IX]]
    if settings.IS_DEVELOPMENT:
        test_ground_truths = test_ground_truths[[PRED_IX]]

    # Load the trained model
    print("\n--- Loading trained model: {}".format(model_name_from_arguments()))

    # Create the UNet model and load its saved weights
    unet = UNet_NN(img_height=settings.IMG_HEIGHT,
                   img_width=settings.IMG_WIDTH,
                   img_channels=settings.IMG_CHANNELS,
                   num_classes=settings.NUM_CLASSES)
    model = unet.build_model_softmax()
    # model = unet.build_model_sigmoid()
    model.load_weights(model_name_from_arguments())
    model.summary()

    # Make predictions
    print("\n--- Making predictions")
    predictions = model.predict(test_imgs, batch_size=settings.TRN_BATCH_SIZE, verbose=2)

    # print(predictions[0, 100:110, 100])
    # predictions = np.where(predictions > 0.9, 1., 0.)

    # Convert predictions to images
    predictions = convert_pred_to_img(predictions, settings.TRN_PRED_THRESHOLD)
    # print(" predictions.shape AFTER conv: {} ".format(predictions.shape))

    if settings.IS_DEVELOPMENT:
        tmp_img = test_ground_truths[0]
        cv2.imshow("Ground truth", tmp_img)
        print("gr truth max {} type {}".format(np.max(tmp_img), tmp_img.dtype))

        tmp_img = test_imgs[0]
        cv2.imshow("Original", tmp_img)
        print("original {} type {}".format(np.max(tmp_img), tmp_img.dtype))

        tmp_img = predictions[0]
        cv2.imshow("Prediction", tmp_img)
        print("prediction {} type {}".format(np.max(tmp_img), tmp_img.dtype))
        cv2.waitKey(0)

    print("\n--- Producing output images")
    if settings.IS_DEVELOPMENT:
        group_images(test_ground_truths[0:9], 3, 255, False, "../output/DECISION_"+unet.title+"_grp_originals")
    group_images(test_imgs[0:9], 3, 1.0, False, "../output/DECISION_" + unet.title+"_grp_images")
    group_images(predictions[0:9], 3, 1.0, False, "../output/DECISION_" + unet.title+"_grp_predictions")

    print("\n--- Predicting complete")
