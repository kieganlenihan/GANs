import numpy as np
import sys
sys.path.append("/home/kiegan/Documents/stylegan2-ada")
import pickle
import dnnlib
import dnnlib.tflib as tflib
import PIL.Image
from tqdm import tqdm
from math import ceil

class GAN_visualization:
    def __init__(self, path, n_img_x, n_img_y, trunc):
        self.seeds = np.random.randint(1e7, size = n_img_x * n_img_y)
        self.get_model(path)
        self.generate_latent_vectors()
        self.get_tf_noise_vars()
        self.trunc = trunc
        self.n_img_x = n_img_x
        self.n_img_y = n_img_y
    def get_model(self, path):
        stream = open(path, "rb")
        tflib.init_tf()
        with stream:
            G, D, Gs = pickle.load(stream, encoding = "latin1")
        self.Gs = Gs
    def generate_latent_vectors(self):
        zs = []
        for idx, seed in enumerate(self.seeds):
            rand = np.random.RandomState(seed)
            z = rand.randn(1, *self.Gs.input_shape[1:])
            zs.append(z)
        self.zs = zs
    def get_tf_noise_vars(self):
        noise = [var for name, var in self.Gs.components.synthesis.vars.items() if name.startswith("noise")]
        self.noise_vars = noise
    def generate_images(self):
        Gs_kwargs = dnnlib.EasyDict()
        Gs_kwargs.output_transform = dict(func = tflib.convert_images_to_uint8, nchw_to_nhwc = True)
        Gs_kwargs.randomize_noise = False
        if not isinstance(self.trunc, list):
            trunc = [self.trunc] * len(self.zs)
        imgs = []
        for idx, z in tqdm(enumerate(self.zs)):
            Gs_kwargs.trunc = trunc[idx]
            noise = np.random.RandomState(1)
            tflib.set_vars({var: noise.randn(*var.shape.as_list()) for var in self.noise_vars})
            images = self.Gs.run(z, None, **Gs_kwargs)
            imgs.append(PIL.Image.fromarray(images[0], "RGB"))
        return imgs
    def generate_image_grid(self, imgs, scale = 1):
        w, h = imgs[0].size
        w = int(w * scale)
        h = int(h * scale)
        height = self.n_img_y * h
        width = self.n_img_x * w
        grid = PIL.Image.new("RGBA", (width, height), "white")
        for i, img in enumerate(imgs):
            img = img.resize((w, h), PIL.Image.ANTIALIAS)
            grid.paste(img, (w * (i % self.n_img_x), h * (i // self.n_img_y)))
        return grid

if __name__ == "__main__":
    path ="GANs/Models/Biked/00003-tfrecords-res512-auto1-bgcfnc/network-snapshot-001280.pkl"
    vis = GAN_visualization(path, 3, 3, 0.5)
    imgs = vis.generate_images()
    grid = vis.generate_image_grid(imgs)
    grid.show()
    
    
