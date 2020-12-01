import argparse
import numpy as np

import common
import yuv_pb2

from gabriel_protocol import gabriel_pb2
from gabriel_server import local_engine
from gabriel_server import cognitive_engine


class DisplayEngine(cognitive_engine.Engine):
    def __init__(self, args):
        # Instantiate SRNTT model
        self.srntt = SRNTT(
            srntt_model_path=args.srntt_model_path,
            vgg19_model_path=args.vgg19_model_path,
            save_dir=args.save_dir,
            num_res_blocks=args.num_res_blocks,
        )
        print("SRNTT model initialized.")

    def handle(self, input_frame):
        yuv = np.frombuffer(input_frame.payloads[0], dtype=np.uint8)

        to_server = cognitive_engine.unpack_extras(yuv_pb2.ToServer,
                                                   input_frame)
        width = to_server.width
        height = to_server.height
        rotation = to_server.rotation

        yuv = np.reshape(yuv, ((height + (height//2)), width))
        img = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_NV21)

        if rotation != 0:
            # np.rot90(img, 3) would correctly display an image rotated 90
            # degress from Android
            times_to_rotate = (360 - rotation) / 90
            img = np.rot90(img, times_to_rotate)

        print(f"DISPLAYENGINE HANDLER: INPUT FRAME TYPE -- {type(img)} -- {isinstance(img, np.ndarray)}")

        # TODO: Run test without reference on input image
        srntt_frame = self.srntt.test_without_ref(
            input_dir=img,
            ref_dir=None,
            use_pretrained_model=True,
            use_init_model_only=False,
            use_weight_map=False,
            result_dir="SRNTT/demo_testing_srntt",
            ref_scale=1.0,
            is_original_image=True
            # input_dir=args.input_dir,
            # ref_dir=args.ref_dir,
            # use_pretrained_model=args.use_pretrained_model,
            # use_init_model_only=args.use_init_model_only,
            # use_weight_map=args.use_weight_map,
            # result_dir=args.result_dir,
            # ref_scale=args.ref_scale,
            # is_original_image=args.is_original_image
        )

        # PREV structure
        status = gabriel_pb2.ResultWrapper.Status.SUCCESS
        result_wrapper = cognitive_engine.create_result_wrapper(status)

        result = gabriel_pb2.ResultWrapper.Result()
        result.payload_type = gabriel_pb2.PayloadType.IMAGE
        result.payload = srntt_frame
        result_wrapper.results.append(result)

        return result_wrapper


def main():
    print("I am here")
    common.configure_logging()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'source_name', nargs='?', default=common.DEFAULT_SOURCE_NAME)
    
    # Initialization Parameters
    parser.add_argument('--srntt_model_path', type=str, default='SRNTT/SRNTT/models/SRNTT')
    parser.add_argument('--vgg19_model_path', type=str, default='SRNTT/SRNTT/models/VGG19/imagenet-vgg-verydeep-19.mat')
    parser.add_argument('--save_dir', type=str, default=None, help='dir of saving intermediate training results')
parser.add_argument('--num_res_blocks', type=int, default=16, help='number of residual blocks')

    # Test Parameters
    # parser.add_argument('--result_dir', type=str, default='result', help='dir of saving testing results')
    # parser.add_argument('--ref_scale', type=float, default=1.0)
    # parser.add_argument('--is_original_image', type=str2bool, default=True)
    
    args = parser.parse_args()

    def engine_factory():
        return DisplayEngine(args)

    local_engine.run(engine_factory, args.source_name, input_queue_maxsize=60,
                     port=common.WEBSOCKET_PORT, num_tokens=2)


if __name__ == '__main__':
    main()
