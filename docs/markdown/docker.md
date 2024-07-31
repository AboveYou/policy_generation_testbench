# Docker
How to recreate the environment using the exported Docker images.

## import
```bash
docker load -i <input_file.tar>
```

## export
```bash
docker save -o <output_file.tar> <image_name:tag>
```

Optionally multiple images can be exported:
```bash
docker save -o <output_file.tar> <image1:tag> <image2:tag>
```
