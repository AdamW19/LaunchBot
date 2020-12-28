# From Splatbot: https://github.com/ktraw2/SplatBot/blob/master/modules/gif_generator.py

import datetime
from modules.async_client import AsyncClient
from modules.splatoon_rotation import SplatoonRotation, ModeTypes
from modules.execute import render_gif


async def generate_gif(rotation_info: SplatoonRotation, channel_id: str, bot):
    # Making sure we have the images to put together
    if rotation_info is None or rotation_info.stage_a_image is None or rotation_info.stage_b_image is None or \
            (rotation_info.splatfest is not None and rotation_info.splatfest.stage_c_image is None):
        raise AttributeError("Files to generate gif does not exist")

    # setting up the image name and image/gif file names
    if rotation_info.mode_type is ModeTypes.SPLATFEST:
        image_c = rotation_info.splatfest.stage_c_image
    else:
        image_c = None
    image_a = rotation_info.stage_a_image
    image_b = rotation_info.stage_b_image
    image_base = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-" + str(channel_id)

    image_a_filename = image_base + "-1.png"
    image_b_filename = image_base + "-2.png"

    if image_c is not None:
        image_c_filename = image_base + "-3.png"
    else:
        image_c_filename = None

    gif_filename = image_base + ".gif"

    # getting the images and saving them locally
    client = AsyncClient(session=bot.session)
    await client.send_image_request(image_url=image_a, file_path=image_a_filename)
    await client.send_image_request(image_url=image_b, file_path=image_b_filename)
    if image_c_filename is not None:
        await client.send_image_request(image_url=image_c, file_path=image_c_filename)

    # making the gif
    await render_gif(image_base, gif_filename)

    # returning the name of the gif on file
    return gif_filename
