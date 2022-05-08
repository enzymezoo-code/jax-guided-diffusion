import numpy as np
import jax
import jax.numpy as jnp
import jax.scipy as jsp
import jaxtorch
from jaxtorch import PRNG, Context, Module, nn, init

import clip_jax

from diffusion_models.common import *
from diffusion_models.schedules import cosine

@jax.tree_util.register_pytree_node_class
class Perceptor(object):
    # Wraps a CLIP instance and its parameters.
    def __init__(self, image_fn, text_fn, clip_params, preprocess):
        self.image_fn = image_fn
        self.text_fn = text_fn
        self.clip_params = clip_params
        self.preprocess = preprocess
    @jax.jit
    def embed_cutouts(self, cutouts):
        return norm1(self.image_fn(self.clip_params, cutouts))
    def embed_text(self, text):
        tokens = clip_jax.tokenize([text])
        text_embed = self.text_fn(self.clip_params, tokens)
        return norm1(text_embed.squeeze(0))
    def embed_texts(self, texts):
        return jnp.stack([self.embed_text(t) for t in texts])
    def embed_image(self, init_pil):
        image_embed = self.image_fn(self.clip_params, np.expand_dims(self.preprocess(init_pil), 0))
        return image_embed
    def tree_flatten(self):
        return [self.clip_params], [self.image_fn, self.text_fn, self.preprocess]
    def tree_unflatten(static, dynamic):
        [clip_params] = dynamic
        [image_fn, text_fn, preprocess] = static
        return Perceptor(image_fn, text_fn, clip_params, preprocess)

clip_size = 224
normalize = Normalize(mean=[0.48145466, 0.4578275, 0.40821073],
                      std=[0.26862954, 0.26130258, 0.27577711])

image_fn, text_fn, clip_params, preprocess = clip_jax.load('ViT-B/32')
vit32 = Perceptor(image_fn, text_fn, clip_params, preprocess)
image_fn, text_fn, clip_params, preprocess = clip_jax.load('ViT-B/16')
vit16 = Perceptor(image_fn, text_fn, clip_params, preprocess)
def get_vitl14():
    image_fn, text_fn, clip_params, preprocess = clip_jax.load('ViT-L/14')
    vitl14 = Perceptor(image_fn, text_fn, clip_params, preprocess)
    return vitl14
def get_vitl14_336px():
    image_fn, text_fn, clip_params, preprocess = clip_jax.load('ViT-L/14@336px')
    vitl14_336px = Perceptor(image_fn, text_fn, clip_params, preprocess)
    return vitl14_336px 
