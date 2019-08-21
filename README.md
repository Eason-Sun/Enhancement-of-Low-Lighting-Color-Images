# Enhancement-of-Low-lighting-Color-Images

## Problem Definition:
In daily uses of consumer cameras, insufficient illumination can easily cause image illegibility and poor contrast, which are arguably the most common and annoying type of image degradations, much more so than noises and insufficient resolution.

## Root Cause:
In low lighting conditions, the irradiance that a camera receives from scenes is attenuated along the line of sight. In addition, the incoming light is blended with the air light. As a result, the images captured by cameras are degraded and the contrast is lost.

## Hardware solutions:
1) Infrared camera system detects objects by the radiation objects’ temperature emit based on high spectrum range. The thermal imaging device will still function even in complete darkness. In fact, the diference is very subtle when comparing thermal images taken during
day and at night. When it comes to objects that easily adopt to the surrounding temperature, for example, traffic signs, road markings, the infrared camera system will probably not yield a desired result, since it will be difficult for this system to diferentiate these objects from surroundings.

2) From photography, we know the famous exposure triangle: aperture, shutter speed and ISO. These are the most basic tools to control exposure. Under low-lighting conditions, we may choose an larger aperture to obtain the appropriate exposure. However, a wide open aperture will usually lead a very shallow depth of feld, and in some particular camera system, it’s not a option such that the aperture could not be adjust independently. We could also consider increasing the ISO of the sensor. In such case, the side efect will be the noise introduced in image. The amount of noise is depending of lots of factors, for example, the size of the sensor, the structure of the camera housing and most importantly, the quality of the sensor itself. Lastly, we could try to slow down the shutter speed. This would work really well in the most situations. This often requires extra equipment (e.g. Tripod). However, when the targeting object does not remain still, long exposure will create blurry motion which is not always wanted depending on the applications.

3) Using external lighting equipment (like fash light) is another approach, but it will not be practical for recording far distanced scenes.

## Software solutions:

### Test Image:
![CoE_4TN4_Project_2_Report](https://user-images.githubusercontent.com/29167705/63470087-b0ce4980-c439-11e9-905c-31e104d1f438.jpg)

### Approach 1: HDR
HDR processing becomes very useful when the images get underexposed due to limited dynamic range. (e.g. At sunset, if the sky is properly exposed, any foreground objects will appear too dark.) HDR will process a burst of images with diferent exposure settings, and
combines them into a single image. This process will get the proper exposure for both dark end and bright end. In addition, it will also reduce noise by combining images.

### Approach 2: Gamma correction
It maps a narrow range of the input intensity levels (dark end) to a broader range of the output intensity levels, at the same time, it compress the bright end of the input, which yields a brighter image.

### Approach 3: Histogram equalization
It is one of the most general approach to enhance low-light images. It stretches the dynamic range of the dark end to cover a wider range of the grey scale values.

### Comparison:

![Capture](https://user-images.githubusercontent.com/29167705/63471694-e6753180-c43d-11e9-936c-289c966b8b7d.JPG)


1) Gamma correction stretches the darker area and compresses the brighter area by setting
(gamma < 1). The overall brightness has been greatly improved in those test images.
However, all of the images sufer from wash out effects, which means they lose contrasts. If
we examine their histogram carefully. We could observe that even though the gamma
correction tries to spread out the intensity distribution, the overall histogram is still
unbalanced under the whole dynamic range.

2) Global histogram equalization method grantees the relatively fat output histogram such
that the result images become brighter and very contrasty. The problem with this method is
that the transformation function is evaluated based on the intensity distribution of the
entire image, the enhancement will be applied globally, which implies that it will generally
fail to enhance details over small areas in an image since the number of pixels in small areas
have negligible infuence on the computation of global transformation. From those images
above, we can clearly see the signifcant enhancement of noise and a large amount of false
colour produced by this method, at the same time, there is almost no new signifcant details
revealed from the original. As the result, the overall images look noisy and over-saturated.

3) Local histogram equalization provides a solution for the problems mentioned above. It
devises transformation function based on intensity distribution of pixel neighbourhood.
This procedure is to define a neighbourhood and move its centre from pixel to pixel in a
horizontal or vertical manner. For each centre, the histogram equalization transformation
function is computed by the neighbourhood pixel and will apply to the centre pixel. 
The process will repeat by shifting centres. Now we can observe that the signifcant details are
revealed with minimal noise present by using local histogram equalization comparing to
global histogram equalization.

## Problem with HE:
Without taking tonality into consideration, histogram equalization will sometimes reduce the dynamic range and present poor perceptual image quality
![Capture](https://user-images.githubusercontent.com/29167705/63471044-32bf7200-c43c-11e9-8fe2-fd3456e66a1a.JPG)

## Solution: Optimal Contrast-Tone Mapping (OCTM)
Since pixel values are discrete, histogram is an approximation to a PDF, and no new allowed
intensity levels are created in this process, thus, it is not rare to see many-to-one intensity
levels’ mappings. Therefore, this process might reduce the number of possible intensity
levels of the original image, which results in loss of tonality. If we look at the sun ray from
the above crop images, we can easily capture discrete colour banding and sharp transition
edges from the HE.

Instead of maximizing the total contrast alone, OCTM introduces a constrained
optimization solution to achieve high contrast and subtle tone reproduction with precise
control according to users’ preferences and applications. The OCTM algorithm can be
implemented by using linear programming.

The constrained optimization can be formulate below:

![Capture](https://user-images.githubusercontent.com/29167705/63471179-7914d100-c43c-11e9-9fb0-d6ee727cac42.JPG)

where,
L is the dynamic range of the input image  
L is the dynamic range of the output image  
pj is the probability that a pixel in input image has a grey level j  
sj is the increment in output intensity versus a unit step up in input level j

The optimization equalization states that our goal is to maximize the contrast gain of the
input image by maximize the sum of the diference among all subsequent intensity levels.  
The condition (1) ensures the output intensity levels are inside the output dynamic range L.  
The condition (2) ensures the transfer function is monotonically increasing.  
The condition (3) specifes the maximum number of steps of non-increasing intensity levels,
which controls the tone continuity.

In my implementation, I found that the three conditions listed above are not enough to
recover super dark images. Below is the histogram of test image 1:  
![Capture](https://user-images.githubusercontent.com/29167705/63471516-58994680-c43d-11e9-8777-effc1125a9c1.JPG)

I found that the most dominant intensity levels range from 0 to 7 and there is no pixel has grey level that is greater than 52. Therefore, extra constraints are essential to add into this optimization computation
process.  
My proposed constraints are:  
![Capture](https://user-images.githubusercontent.com/29167705/63471610-9c8c4b80-c43d-11e9-8bd8-71944fe80d01.JPG)

### Comparison 1: Low Light Recovery

![Capture](https://user-images.githubusercontent.com/29167705/63471803-30f6ae00-c43e-11e9-9926-0bd202401604.JPG)

### Comparison 2: Tonality Preserving

![Capture](https://user-images.githubusercontent.com/29167705/63471973-b1b5aa00-c43e-11e9-83c2-9eb767540b83.JPG)

The tonality of the image is preserved so that the signifcant of details are revealed from the original degraded image. The oversaturation and false colour from HE gets solved in some sense. Noise ratio is also efectively attenuated. From the last
comparison, the colour banding and sharp transition get handled properly in OCTM.

## Conclusion:
If we view the increment in intensity levels (sj) as a scarce resource, sacrifce of the absolute
contrast gain will improve the tonality by allocating the dynamic range increments more
evenly over the histogram and avoiding many-to-one pixel mapping.
The OCTM can be very well formulated and implemented by using linear programming, at
the same time, it provides the freedom to users so that they could fne tune the parameters
for individual perceptual expectations and specifc applications.


