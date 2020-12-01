import argparse
import cv2

import common
# from .utils.cropAtCenter import cropImageCenter
# from cropAtCenter import cropImageCenter

from gabriel_client.websocket_client import WebsocketClient
from gabriel_client.opencv_adapter import OpencvAdapter

DEFAULT_SERVER_HOST = '128.2.212.50'
DEFAULT_ZOOM_FACTOR = 10

def preprocess(frame):
    # return frame

    print(type(frame))

    width, height = frame.shape[1], frame.shape[0]

    left = int(width/2 * (1 - 1/DEFAULT_ZOOM_FACTOR))
    top = int(height/2 * (1 - 1/DEFAULT_ZOOM_FACTOR))
    right = int(width/2 * (1 + 1/DEFAULT_ZOOM_FACTOR))
    bottom = int(height/2 * (1 + 1/DEFAULT_ZOOM_FACTOR))

    cropped_frame = frame[top:bottom, left:right]
    return cropped_frame


def produce_extras():
    return None


def consume_frame(frame, _):
    cv2.imshow('Image from server', frame)
    cv2.waitKey(1)


def main():
    common.configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source_name', nargs='?', default=common.DEFAULT_SOURCE_NAME)
    parser.add_argument('server_host', nargs='?', default=DEFAULT_SERVER_HOST)
    args = parser.parse_args()

    capture = cv2.VideoCapture(0)
    opencv_adapter = OpencvAdapter(
        preprocess, produce_extras, consume_frame, capture, args.source_name)

    client = WebsocketClient(
        args.server_host, common.WEBSOCKET_PORT,
        opencv_adapter.get_producer_wrappers(), opencv_adapter.consumer)
    client.launch()


if __name__ == '__main__':
    main()
