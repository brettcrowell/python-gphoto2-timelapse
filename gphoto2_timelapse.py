from timelapse import Timelapse
import gphoto2 as gp
import os

class GPhoto2Timelapse(Timelapse):

    def take_picture(self, image):

        image_filename = "{}-{}".format(image['name'], image['ts'])

        print("Capturing image `{}`".format(image_filename))

        context = gp.gp_context_new()
        camera = gp.check_result(gp.gp_camera_new())
        target = None

        try:

            # initialize the camera
            gp.check_result(gp.gp_camera_init(camera, context))

            # save information about found camera
            # print(gp.check_result(gp.gp_camera_get_summary(camera, context)))

            # capture image, making note of the file path on memory card
            file_path = gp.check_result(gp.gp_camera_capture(camera, gp.GP_CAPTURE_IMAGE, context))

            print('Camera file path: {0}/{1}'.format(file_path.folder, file_path.name))

            # get reference to image file on camera
            camera_file = gp.check_result(gp.gp_camera_file_get(camera,
                                                                file_path.folder,
                                                                file_path.name,
                                                                gp.GP_FILE_TYPE_NORMAL,
                                                                context))

            # determine where to store this file locally
            target = os.path.join(self.preferences['location'], "output", "{}.jpg".format(image_filename))

            print('Copying image to', target)

            # download image to directory determined above
            gp.check_result(gp.gp_file_save(camera_file, target))

            # @todo need to check file size here

        except gp.GPhoto2Error as ex:

            if ex.code == gp.GP_ERROR_MODEL_NOT_FOUND:
                print("Unable to find usable camera.  Is it connected, alive, and awake? ({})".format(ex.string))

            elif ex.code == gp.GP_ERROR_IO_USB_CLAIM:
                print("Camera is already in use.  If on Mac, try running `sudo killall PTPCamera` ({})".format(ex.string))
                self.killall_ptp(image)

            elif ex.code == gp.GP_ERROR_IO:
                print ("I/O issue with camera, USB connection needs to be reset ({})".format(ex.string))
                self.reset_usb(image)

            else:
                print("GPhoto2 Error: {}".format(ex.string))
                self.reboot_machine(image)

        finally:

            # let go of the camera now
            gp.check_result(gp.gp_camera_exit(camera, context))

        return target