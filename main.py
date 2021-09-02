from visualize_GAN_performance import GAN_visualization
        

if __name__ == "__main__":
    path ="/path/to/pkl/file"
    vis = GAN_visualization(path, 3, 3, 0.5)
    vecs = vis.generate_latent_vectors_n(2)
    imgs = vis.generate_imgs(vis.interpolate(vecs, 9))
    grid = vis.generate_image_grid(imgs)
    grid.show()
    vid = GAN_visualization(path, 3, 3, 0.9)
    vid.set_vid_params()
    vid.generate_all_latents()
    f_name = "/path/to/result/folder/random_grid_%s_%.2f.mp4" % (vid.random_seed, vid.trunc)
    vid.generate_video(f_name)
    
    
