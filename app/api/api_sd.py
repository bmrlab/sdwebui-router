from fastapi import APIRouter, Depends
from app.core.pool import BusyException
from loguru import logger
from .model import ResponseModel, RWModel
from .api_auth import get_current_user

router = APIRouter()


class GenImg(RWModel):
    mode: str = "txt2img"
    prompt: str = ""
    setup_params: dict = {}
    sd_params: dict


@router.post("/gen")
def gen_img(item: GenImg, current_user: str = Depends(get_current_user)):
    logger.info(f"start gen_img: {item}")
    from app import pool

    try:
        ckpt_model_name = item.setup_params.get("base_model", {}).get("name", "")
        controlnet_model_list = [
            unit["model"] for unit in item.sd_params.get("controlnet_units", [])
        ]
        res = pool.pick(ckpt_model_name, controlnet_model_list)
        data = res.process(item)
        return ResponseModel(data=data)
    except BusyException as e:
        return ResponseModel(data={}, status=203, message=f"{e}")
    except Exception as e:
        logger.exception(e)
        return ResponseModel(data={}, status=500, message=f"{e}")


@router.post("/submit")
def submit(item: GenImg,
           current_user: str = Depends(get_current_user)
           ):
    """
    提交生成请求
    :param item:
    # :param current_user:
    :return:
    """
    logger.info(f"start gen_img: {item}")
    from app import pool

    try:
        ckpt_model_name = item.setup_params.get("base_model", {}).get("name", "")
        controlnet_model_list = [
            unit["model"] for unit in item.sd_params.get("controlnet_units", [])
        ]
        res = pool.pick(ckpt_model_name, controlnet_model_list)
        gen_id = res.async_process(item)
        return ResponseModel(data={"gen_id": gen_id})
    except BusyException as e:
        return ResponseModel(data={}, status=203, message=f"{e}")
    except Exception as e:
        logger.exception(e)
        return ResponseModel(data={}, status=500, message=f"{e}")


@router.get("/query/{gen_id}")
def query(gen_id):
    """
    查询异步处理结果
    :param gen_id:
    :return:
    """
    from app.core.pool import mem_storage
    item = mem_storage.get_data_item(gen_id=gen_id)
    if item:
        return ResponseModel(data=item.to_dict())
    else:
        return ResponseModel(data={})


@router.get("/progress/{gen_id}")
def progress(gen_id):
    """
    查询过程结果数据
    :param gen_id:
    :return:
    """
    from app.core.pool import mem_storage, WEBUI_USERNAME, WEBUI_PASSWORD
    from webuiapi import WebUIApi
    try:
        item = mem_storage.get_data_item(gen_id)
        if item:
            webuiapi = WebUIApi(baseurl=f"{item.origin}/sdapi/v1", username=WEBUI_USERNAME, password=WEBUI_PASSWORD)
            info = webuiapi.get_progress()

            return ResponseModel(data=info)
        else:
            return ResponseModel(data={}, status=404, message=f"not found gen_id record: {gen_id}")
    except Exception as e:
        logger.exception(e)
        return ResponseModel(data={}, status=500, message=f"{e}")
