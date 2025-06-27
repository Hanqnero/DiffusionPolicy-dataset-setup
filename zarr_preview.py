import zarr

def print_zarr_group(group, indent=''):
    for key in group.keys():
        print(f"{indent}- {key}")
        item = group[key]
        if isinstance(item, zarr.Group):
            print_zarr_group(item, indent + '  ')
        elif isinstance(item, zarr.Array):
            print(f"{indent}  Shape: {item.shape}, Dtype: {item.dtype}")
            print(f"{indent}  First 5 elements:\n{item[:5]}")

z = zarr.open("new_replay_buffer.zarr", mode='r')
print_zarr_group(z)

print(list(z.keys()))

print(z['data']['timestamp'][:5])