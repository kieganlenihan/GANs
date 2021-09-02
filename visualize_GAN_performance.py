import numpy as np
import sys
sys.path.append("/home/kiegan/Documents/stylegan2-ada")
import pickle
import dnnlib
import dnnlib.tflib as tflib
import PIL.Image
from tqdm import tqdm
from math import ceil
import scipy
import moviepy.editor


class GAN_visualization:
    def __init__(self, path, n_img_x, n_img_y, trunc):
        self.get_model(path)
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
    def generate_latent_vectors_n(self, n = None):
        if n is None:
            n = self.n_img_x * self.n_img_y
        self.seeds = np.random.randint(1e7, size = n)
        zs = []
        for idx, seed in enumerate(self.seeds):
            rand = np.random.RandomState(seed)
            z = rand.randn(1, *self.Gs.input_shape[1:])
            zs.append(z)
        return zs
    def get_tf_noise_vars(self):
        noise = [var for name, var in self.Gs.components.synthesis.vars.items() if name.startswith("noise")]
        self.noise_vars = noise
    def generate_imgs(self, zs):
        Gs_kwargs = dnnlib.EasyDict()
        Gs_kwargs.output_transform = dict(func = tflib.convert_images_to_uint8, nchw_to_nhwc = True)
        Gs_kwargs.randomize_noise = False
        if not isinstance(self.trunc, list):
            trunc = [self.trunc] * len(zs)
        imgs = []
        for idx, z in tqdm(enumerate(zs)):
            Gs_kwargs.trunc = trunc[idx]
            noise = np.random.RandomState(1)
            tflib.set_vars({var: noise.randn(*var.shape.as_list()) for var in self.noise_vars})
            images = self.Gs.run(z, None, **Gs_kwargs)
            imgs.append(PIL.Image.fromarray(images[0], "RGB"))
        return imgs
    def generate_image_grid(self, imgs, scale = 1, rows = None, cols = None):
        if rows is None:
            rows = self.n_img_x
        if cols is None:
            cols = self.n_img_y
        w, h = imgs[0].size
        w = int(w * scale)
        h = int(h * scale)
        height = rows * h
        width = cols * w
        grid = PIL.Image.new("RGBA", (width, height), "white")
        for i, img in enumerate(imgs):
            img = img.resize((w, h), PIL.Image.ANTIALIAS)
            grid.paste(img, (w * (i % cols), h * (i // cols)))
        return grid
    def interpolate(self, zs, steps):
        out = []
        for i in range(len(zs) - 1):
            for idx in range(steps):
                frac = idx / float(steps)
                out.append(zs[i+1] * frac + zs[i] * (1 - frac))
        return out
    def set_vid_params(self, ft = 20, st = 1, iz = 1, fps = 24):
        self.frame_time = ft
        self.smooth_time = st
        self.zoom = iz
        self.fps = fps
        self.random_seed = np.random.randint(0, 999)
        self.nframes = int(np.rint(self.frame_time * self.fps))
        self.random_state = np.random.RandomState(self.random_seed)
    def generate_all_latents(self):
        shape = [self.nframes, np.prod([self.n_img_x, self.n_img_y])] + self.Gs.input_shape[1:]
        zs = self.random_state.randn(*shape).astype(np.float32)
        zs = scipy.ndimage.gaussian_filter(zs, [self.smooth_time * self.fps] + [0] * len(self.Gs.input_shape), mode = "wrap")
        zs /= np.sqrt(np.mean(np.square(zs)))
        self.zs = zs
    def get_img_grid(self, imgs):
        n, img_h, img_w, ch = imgs.shape
        grid_w = self.n_img_x * img_w
        grid_h = self.n_img_y * img_h
        grid = np.zeros([grid_h, grid_w, ch], dtype = imgs.dtype)
        for i in range(n):
            x = (i % self.n_img_y) * img_w
            y = (i // self.n_img_y) * img_h
            grid[y : y + img_h, x : x + img_w] = imgs[i]
        if self.zoom > 1:
            grid = scipy.ndimage.zoom(grid, [self.zoom, self.zoom, 1], order = 0)
        if grid.shape[2] == 1:
            grid = grid.repeat(3, 2)
        return grid
    def generate_frame(self, t):
        frame_idx = int(np.clip(np.round(t * self.fps), 0, self.nframes - 1))
        latent_vecs = self.zs[frame_idx]
        fmt = dict(func = tflib.convert_images_to_uint8, nchw_to_nhwc = True)
        imgs = self.Gs.run(latent_vecs, None, truncation_psi = self.trunc, randomize_noise = False, output_transform = fmt, minibatch_size = 16)
        grid = self.get_img_grid(imgs)
        return grid
    def generate_video(self, out_path):
        video = moviepy.editor.VideoClip(self.generate_frame, duration = self.frame_time)
        video.write_videofile(out_path, fps = self.fps)