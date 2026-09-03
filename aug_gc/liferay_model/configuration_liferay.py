from transformers import PretrainedConfig

class LiferayConfig(PretrainedConfig):
    """Configuration class for the xenτₖ Liferay Compositional Model."""
    model_type = "liferay"

    def __init__(
        self,
        f_0=936.0,
        minor_third=0.8333333333,
        liferay_teeth=12,
        leaf_initial=0.365,
        shade_initial=0.4,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.f_0 = f_0
        self.minor_third = minor_third
        self.liferay_teeth = liferay_teeth
        self.leaf_initial = leaf_initial
        self.shade_initial = shade_initial
