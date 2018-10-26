#!/software/conda/bin/python3

import argparse
import numpy as np
import os.path

import fitsio
import cv2
import netpbmfile

def trimFile(filename, xrange=None, yrange=None):
    print(f"reading {filename}")
    frame = fitsio.read(filename, ext='IMAGE')
    if yrange is not None:
        frame = frame[yrange[0], yrange[1]]
    if xrange is not None:
        frame = frame[:,xrange[0]:xrange[1]]

    return frame

def normImage(img, dtype='u16'):
    if dtype == 'u8':
        maxOut = 255
    elif dtype == 'u16':
        maxOut = 65535
    else:
        raise ValueError("bad dtype")

    maxval = 1.0 * img.max()
    return (maxval/img * maxOut).astype('u8')

def convertFiles(files, dtype=None):
    for image_path in files:
        path, _ = os.path.splitext(image_path)
        path = os.path.basename(path)
        frame = trimFile(image_path)
        frame = normImage(frame, dtype=dtype)

        netpbmfile.imsave(f"{path}.pgm", frame)

def makeMovie(files, outname, dtype=None):
    # Determine the width and height from the first image
    frame = trimFile(files[0])
    height, width = frame.shape

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'RAW ') # Be sure to use lower case
    out = cv2.VideoWriter(outname, fourcc, 12.0, (width, height), isColor=False)

    for image_path in files:
        path, _ = os.path.splitext(image_path)
        path = os.path.basename(path)
        frame = trimFile(image_path)
        frame = normImage(frame, dtype=dtype)

        print(f"shape: {frame.shape}")
        out.write(frame) # Write out frame to video

    # Release everything if job is finished
    out.release()

    print(f"The output video is {outname}")

def main(argv=None):
    if argv is None:
        import sys
        argv = sys.argv[1:]
    if isinstance(argv, str):
        import shlex
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", required=True, default='output.mp4', help="output video file")
    parser.add_argument('--movie', action='store_true', help='convert to movie')
    parser.add_argument('--convert', action='store_true', help='convert to files')
    parser.add_argument('files', metavar='N', nargs='+', help='filename to stream together')
    args = parser.parse_args(argv)

    if args.movie and args.convert:
        raise RuntimeError("specify exactly one of --movie or --convert")
    if not (args.movie or args.convert):
        raise RuntimeError("specify exactly one of --movie or --convert")

    files = args.files

if __name__ == '__main__':
    main()
