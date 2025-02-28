import os

def file_generator(root_dir, exclude_list):
    """
    遍历项目路径下的所有文件，排除指定目录或文件，生成相对路径的字符串生成器。

    :param root_dir: 要遍历的根目录路径
    :param exclude_list: 排除的目录或文件的相对路径列表
    :return: 生成器，生成相对于root_dir的文件路径字符串
    """
    exclude_set = set(exclude_list)
    root_dir = os.path.abspath(root_dir)  # 确保根目录为绝对路径

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # 计算当前目录相对于根目录的路径
        rel_dir = os.path.relpath(dirpath, root_dir)

        # 排除当前目录本身在排除列表中
        if rel_dir in exclude_set:
            del dirnames[:]  # 防止遍历子目录
            continue

        # 排除子目录：检查子目录的相对路径是否在排除列表中
        dirs_to_remove = []
        for d in dirnames:
            child_rel = os.path.join(rel_dir, d) if rel_dir != '.' else d
            if child_rel in exclude_set:
                dirs_to_remove.append(d)
        for d in dirs_to_remove:
            dirnames.remove(d)

        # 处理文件：检查文件的相对路径是否在排除列表中
        for filename in filenames:
            file_rel = os.path.join(rel_dir, filename) if rel_dir != '.' else filename
            if file_rel not in exclude_set:
                yield file_rel