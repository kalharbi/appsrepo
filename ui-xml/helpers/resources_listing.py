import os
import os.path


class ResourcesListing(object):
    
    # Return all the layout files inside /res/layout*
    @staticmethod
    def get_all_layout_dirs(apk_root_path):
        apk_res_path = os.path.join(apk_root_path, 'res')
        layout_dirs = []
        if not os.path.exists(apk_res_path):
           return layout_dirs
        for layout_dir in [os.path.join(apk_res_path, d) for d in os.listdir(apk_res_path)]:
            if os.path.isdir(layout_dir) and os.path.basename(layout_dir).lower().startswith('layout'):
                layout_dirs.append(layout_dir)
        return layout_dirs

    # Return all the layout files inside a given layout directory.
    @staticmethod
    def get_all_layout_files(layout_dir_path):
        layout_files = []
        if not os.path.exists(layout_dir_path):
           return layout_files
        for layout_file in [os.path.join(layout_dir_path, f) for f in os.listdir(layout_dir_path)]:
            if layout_file.lower().endswith('.xml'):
                layout_files.append(layout_file)
        return layout_files
