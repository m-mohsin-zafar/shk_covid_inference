from commons import Commons


class Inference:

    def __init__(self):
        self.class_to_name = {
            0: 'Non Corona',
            1: 'Corona'
        }
        self.utils = Commons()
        self.model = self.utils.prepare_model()

    def get_prediction(self, image_bytes):
        try:
            proc_img = self.utils.preprocess(image_bytes)
            output = self.model.forward(proc_img)
        except Exception:
            return 0, 'error in getting prediction!'
        conf_scr, prediction = output.max(1)
        pred_class = prediction.item()
        pred_cls_name = self.class_to_name[pred_class]
        return pred_class, pred_cls_name, conf_scr
