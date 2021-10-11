import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
from matplotlib.widgets import Button

import cv2
import easygui as eg
import openpyxl

import spot_position_mod as spm

# global variables are used inside the functions because slider.on_changed
# and button.on_clicked are not allowing arguments in called functions

# results_loc = 'C:\\Users\\cgillies.UCLH\\NHS\\(Canc) Radiotherapy - PBT Physics Team - PBT Physics Team\\QAandCommissioning\\Routine QA\\Spot Position\\SpotGrid_Delivered_Results.xlsx'
results_loc = eg.fileopenbox('Please select the results file on sharepoint - \n'
                             'Located in Routine QA/Spot Position')

SPOTSIN3000 = ['Top-Left', 'Top-Centre', 'Top-Right',
               'Left', 'Centre', 'Right',
               'Bottom-Left', 'Bottom-Centre', 'Bottom-Right'
               ]

SPOTSIN4000 = ['Top-Top-Left', 'Top-Top-Centre', 'Top-Top-Right',
               'Top-Left', 'Top-Centre', 'Top-Right',
               'Left', 'Centre', 'Right',
               'Bottom-Left', 'Bottom-Centre', 'Bottom-Right',
               'Bottom-Bottom-Left', 'Bottom-Bottom-Centre',
               'Bottom-Bottom-Right'
               ]

def image_open_blur():
    '''Opens full image, converts to greyscale and adds blur
    '''
    global original
    global blurred
    global activescript
    global output

    image_path = eg.fileopenbox("Please pick a spot image :")
    activescript = spm.ActiveScript(image_path)
    spotpattern = spm.SpotPattern(image_path)
    output = spm.Output(image_path)
    original = spotpattern.image

    print("\nImage dimensions are", original.shape)
    # convert into grayscale
    gray = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)

    # blur with Gaussian kernel
    blurred = cv2.GaussianBlur(gray, (51, 51), 0, cv2.BORDER_ISOLATED)


def image_processing_plotting(threshold, specificity, max_detection_size,
                              nearest_circles, scaling, font_size
                              ):
    '''Initial creation of plot including: original image, processed image
    and detected circles with sliders that can be adjusted and function buttons
    including exporting the spots, loading a new image and changing font size
    '''

    global thresholded
    global eroded
    global dilated
    global circled
    global circles

    thresholded = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)[1]
    eroded = cv2.erode(thresholded, None, iterations=2)
    dilated = cv2.dilate(eroded, None, iterations=2)

    # detect circles in the dilated image
    # 4th parameter: minimum distance between circles,
    # 6th parameter: lowering increases sensitivity but decreases specificity
    circles = cv2.HoughCircles(dilated, cv2.HOUGH_GRADIENT, 1, nearest_circles,
                               param1=50, param2=specificity, minRadius=0,
                               maxRadius=int(max_detection_size)
                               )

    # Order spots by grid position, y is rounded to nearest 10 to enable sort
    circles = np.asarray(sorted(circles[0],
                                key=lambda k: [int(round(k[1], -2)), int(k[0])]
                                )
                         )
    # Expand dimensions to match previous data structure
    circles = np.expand_dims(circles, axis=0)
    # Copy original image to create circled image for display
    circled = original.copy()

    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over the (x, y) coordinates and radius of the circles
        i = 0
        for (x, y, r) in circles:
            i += 1
            # draw the circles over the original image
            cv2.circle(circled, (x, y), int(r*scaling), (0, 255, 0), 4)
            cv2.putText(circled, str(i), (x-int(r*scaling), y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 105, 180), 3
                        )

    plt.subplots_adjust(bottom=0.50)

    plt.subplot(131)
    plt.imshow(original)
    plt.title('Original')

    plt.subplot(132)
    plt.imshow(dilated, cmap='gray')
    plt.title('Thresholded\n& Processed')

    plt.subplot(133)
    plt.imshow(circled, cmap='gray')
    plt.title('Detected Spots')

    plt.show()


# As before but this function will run every time a slider is moved
def image_reprocessing_plotting(val):
    '''Function to update plot after slider values are changed, similar to
    image_processing_plotting function, only one argument can be passed to this
    function, hence the duplication.
    '''
    global thresholded
    global eroded
    global dilated
    global circled
    global circles
    global threshold
    global specificity
    global max_detection_size
    global nearest_circles
    global scaling
    global font_size

    # get values from the sliders
    threshold = threshold_slider.val
    specificity = specificity_slider.val
    max_detection_size = max_detection_size_slider.val
    nearest_circles = nearest_circles_slider.val
    scaling = scaling_slider.val

    thresholded = cv2.threshold(blurred, threshold, 255, cv2.THRESH_BINARY)[1]
    eroded = cv2.erode(thresholded, None, iterations=2)
    dilated = cv2.dilate(eroded, None, iterations=2)

    # detect circles in the thresholded image
    # 4th parameter: minimum distance between circles,
    # 6th parameter: lowering increases sensitivity + decreases the specificity
    circles = cv2.HoughCircles(dilated, cv2.HOUGH_GRADIENT, 1, nearest_circles,
                               param1=50, param2=specificity, minRadius=0,
                               maxRadius=int(max_detection_size)
                               )
    # Order spots by grid position, y is rounded to nearest 10 to enable sort
    circles = np.asarray(sorted(circles[0],
                                key=lambda k: [round(k[1], -2), k[0]]
                                )
                         )
    # Need to expand dimensions to match previous data structure
    circles = np.expand_dims(circles, axis=0)
    # create a copy of the original image to be circled
    circled = original.copy()

    # ensure at least some circles were found
    if circles is not None:
        # convert the (x, y) coordinates and radius of the circles to integers
        circles = np.round(circles[0, :]).astype("int")

        # loop over the (x, y) coordinates and radius of the circles
        i = 0
        for (x, y, r) in circles:
            i += 1
            # draw the circles over the original image
            cv2.circle(circled, (x, y), int(r*scaling), (0, 255, 0), 4)
            cv2.putText(circled, str(i), (x-int(r*scaling), y),
                        cv2.FONT_HERSHEY_SIMPLEX, font_size, (255, 105, 180), 3
                        )

    plt.subplots_adjust(bottom=0.50)

    plt.subplot(131)
    plt.imshow(original)
    plt.title('Original')

    plt.subplot(132)
    plt.imshow(dilated, cmap='gray')
    plt.title('Thresholded\n& Processed')

    plt.subplot(133)
    plt.imshow(circled, cmap='gray')
    plt.title('Detected Spots')

    plt.show()


# font increase/decrease functions, called when relevant buttons are pressed
def increase_font(val):
    '''Button function to increase font size value and update figure
    '''
    global font_size
    font_size += 0.5
    image_processing_plotting(threshold, specificity, max_detection_size,
                              nearest_circles, scaling, font_size
                              )


def decrease_font(val):
    '''Button function to decrease font size value and update figure
    '''
    global font_size
    if font_size > 0.5:
        font_size -= 0.5
        image_processing_plotting(threshold, specificity, max_detection_size,
                                  nearest_circles, scaling, font_size
                                  )


# spot extraction function, called when the relevant button is pressed
def extract(val):
    '''Method to print results to text on console
    '''
    spot_data = {}
    if circles is not None:
        i = 0
        for (x, y, r) in circles:
            i += 1
            # set the exported image boundaries as a square centred on the spot
            y1 = y - int(r * scaling)
            y2 = y + int(r * scaling)
            x1 = x - int(r * scaling)
            x2 = x + int(r * scaling)

            # crop image to edge of original image size
            if y1 < 0:
                y1 = 0
            if x1 < 0:
                x1 = 0

            crop_img = original[y1:y2, x1:x2]

            spot_data[i] = spm.Spot(crop_img[:, :, 0], [x, y], activescript)
            print(i)
            print(spot_data[i])
        write_to_excel = eg.boolbox('Do you want to save to excel?',
                                    title='Option to write data'
                                    )
        if write_to_excel:
            # print('yes')
            list_to_write = [output.datetime]
            list_to_write.extend(spm.select_acquisition_info())
            print(activescript.device)
            list_to_write.append(float(activescript.device))

            # print(f'list to write {list_to_write}')
            wb = openpyxl.load_workbook(results_loc)
            ws = wb.worksheets[0]
            for i in spot_data:
                if activescript.device == '3000':
                    line = list_to_write + [SPOTSIN3000[i-1]]
                if activescript.device == '4000':
                    line = list_to_write + [SPOTSIN4000[i-1]]
                result = spot_data[i].list_results()
                line = line + result
                ws.append(line)
            wb.save(results_loc)
            test = input('Values saved, press enter to continue or C to close')
            if test == 'C':
                raise SystemExit


            # ]

            # cv2.imwrite((save_path+"\\" + str(i)+".tiff"), crop_img)
        # os.startfile(save_path)


def load_new(val):
    '''Method to load new image
    '''
    image_open_blur()
    image_processing_plotting(threshold, specificity, max_detection_size,
                              nearest_circles, scaling, font_size
                              )


def main():
    global threshold_slider
    global scaling_slider
    global specificity_slider
    global max_detection_size_slider
    global nearest_circles_slider
    global font_inc_button
    global font_dec_button
    global extract_button
    global reload_button
    global font_size
    global scaling

    image_open_blur()

    # initialise values with defaults
    threshold = 10
    specificity = 15
    max_detection_size = 100
    nearest_circles = 20
    scaling = 1
    font_size = 2.1

    # plotting sliders and buttons. These are matplotlib widgets.
    # For every item, first a corresponding axis is plotted as a placeholder,
    # then the item itself is defined
    plt.figure("Spot Finder v0.6", figsize=(10., 7.5))

    controls_height = 0.28
    threshold_ax = plt.axes([0.27, controls_height+0.13, 0.5, 0.02])
    specificity_ax = plt.axes([0.27, controls_height+0.1, 0.5, 0.02])
    max_detection_size_ax = plt.axes([0.27, controls_height+0.07, 0.5, 0.02])
    nearest_circles_ax = plt.axes([0.27, controls_height+0.04, 0.5, 0.02])
    scaling_ax = plt.axes([0.27, controls_height+0.01, 0.5, 0.02])

    font_dec_ax = plt.axes([0.85, controls_height+0.11, 0.045, 0.05])
    font_inc_ax = plt.axes([0.905, controls_height+0.11, 0.045, 0.05])
    extract_ax = plt.axes([0.85, controls_height+0.03, 0.1, 0.07])
    reload_ax = plt.axes([0.85, controls_height-0.05, 0.1, 0.07])

    font_dec_button = Button(font_dec_ax, "Font\n-")
    font_inc_button = Button(font_inc_ax, "Font\n+")
    extract_button = Button(extract_ax, "Export\nspots")
    reload_button = Button(reload_ax, "Load new\nimage")

    threshold_slider = Slider(threshold_ax,  # axes object containing slider
                              'Threshold',   # the name of the slider parameter
                              0,             # minimal value of the parameter
                              255,           # maximal value of the parameter
                              valinit=threshold,  # initial value
                              valstep=1,     # discrete step size
                              valfmt="%1.0f",  # printing format
                              dragging=False  # mouse drag inhibits speed
                              )

    specificity_slider = Slider(specificity_ax, 'Specificity', 0, 40,
                                valinit=specificity, valstep=1,
                                valfmt="%1.0f", dragging=False
                                )

    max_detection_size_slider = Slider(max_detection_size_ax,
                                       'Max detection size', 0, 150,
                                       valinit=max_detection_size,
                                       valstep=5, valfmt="%1.0f",
                                       dragging=False
                                       )

    nearest_circles_slider = Slider(nearest_circles_ax,
                                    'Min dist between detected circles', 1,
                                    100, valinit=nearest_circles,
                                    valstep=1, valfmt="%1.0f", dragging=False
                                    )

    scaling_slider = Slider(scaling_ax, 'Extraction size (use last)', 0.4, 5,
                            valinit=scaling, valstep=0.2, valfmt="%1.1f",
                            dragging=False
                            )

    plt.text(0.02, 0.1, "Instructions: "
                        "\n1) Change \"Threshold\" until all spots in the thresholded image are visible and separated."
                        "\n2) Decrease \"Specificity\" until all spots are detected."
                        "\n3) Decrease \"Max detection size\" to get rid of large false detections."
                        "\n4) If more than one detections are made within a spot, increase \"Min dist between detected circles\"."
                        "\n5) Once satisfied, select desirable margin for exported spot images using the \"Extraction size\".",
                        fontsize=12, transform=plt.gcf().transFigure)

    # call the reprocessing function when a slider is moved
    # or the relevant button functions
    # note: "on_changed" only works with one function with one float argument
    # hence the single argument for image_processing_plotting.
    threshold_slider.on_changed(image_reprocessing_plotting)
    scaling_slider.on_changed(image_reprocessing_plotting)
    specificity_slider.on_changed(image_reprocessing_plotting)
    max_detection_size_slider.on_changed(image_reprocessing_plotting)
    nearest_circles_slider.on_changed(image_reprocessing_plotting)
    font_inc_button.on_clicked(increase_font)
    font_dec_button.on_clicked(decrease_font)
    extract_button.on_clicked(extract)
    reload_button.on_clicked(load_new)

    # calling the first iteration of the processing and plotting
    image_processing_plotting(threshold, specificity, max_detection_size,
                              nearest_circles, scaling, font_size
                              )


if __name__ == "__main__":
    main()
