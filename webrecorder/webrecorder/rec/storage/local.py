import os
import shutil

from webrecorder.rec.storage.base import BaseStorage
from webrecorder.rec.storage.storagepaths import add_local_store_prefix, strip_prefix


# ============================================================================
class DirectLocalFileStorage(BaseStorage):
    """Webrecorder storage (local files)."""
    def __init__(self):
        """Initialize Webrecorder storage."""
        super(DirectLocalFileStorage, self).__init__()

        self.storage_root = os.environ['STORAGE_ROOT']

    def delete_collection_dir(self, dir_path):
        """Delete collection directory.

        :param str dir_path: directory path

        :returns: whether successful or not
        :rtype: bool
        """
        local_dir = os.path.join(self.storage_root, dir_path)

        try:
            print('Deleting Directory: ' + local_dir)
            parent_dir = os.path.dirname(local_dir)
            shutil.rmtree(local_dir)
            os.removedirs(parent_dir)
            return True
        except Exception as e:
            print(e)
            return False

    def do_upload(self, target_url, full_filename):
        """Upload file into local file storage.

        :param str target_url: target URL
        :param str full_filename: path

        :returns: whether successful or not
        :rtype: bool
        """
        os.makedirs(os.path.dirname(target_url), exist_ok=True)

        try:
            if full_filename != target_url:
                shutil.copyfile(full_filename, target_url)
            else:
                print('Same File')

            return True
        except Exception as e:
            print(e)
            return False

    def is_valid_url(self, target_url):
        """Return whether given target URL is an existing file.

        :param str target_url: target URL

        :returns: whether given target URL is an existing file
        :rtype: bool
        """
        return os.path.isfile(target_url)

    def get_client_url(self, target_url):
        """Get client URL.

        :param str target_url: target URL

        :returns: client URL
        :rtype: str
        """
        return add_local_store_prefix(target_url.replace(os.path.sep, '/'))

    def client_url_to_target_url(self, client_url):
        """Get target URL (from client URL).

        :param str client URL: client URL

        :returns: target URL
        :rtype: str
        """
        return strip_prefix(client_url)

    def do_delete(self, target_url, client_url):
        """Delete file from storage.

        :param str target_url: target URL

        :returns: whether successful or not
        :rtype: bool
        """
        try:
            print('Deleting: ' + target_url)
            os.remove(target_url)
            #if target_url.startswith(self.storage_root):
            #    os.removedirs(os.path.dirname(target_url))
            return True
        except Exception as e:
            print(e)
            return False


# ============================================================================
class LocalFileStorage(DirectLocalFileStorage):
    """Webrecorder storage w/ Redis interface (local files).

    :ivar StrictRedis redis: Redis interface
    """
    def __init__(self, redis):
        """Initialize Webrecorder storage w/ Redis interface.

        :param StrictRedis redis: Redis interface
        """
        self.redis = redis
        super(LocalFileStorage, self).__init__()

    def delete_collection(self, collection):
        """Delete collection.

        :param collection: collection
        :type: n.s.

        :returns: whether successful or not
        :rtype: bool
        """
        dirpath = os.path.join(self.storage_root, collection.get_dir_path())
        return (self.redis.publish('handle_delete_dir', dirpath) > 0)

    def do_delete(self, target_url, client_url):
        """Delete file.
        
        :param str target_url: target URL
        :param str client_url: client URL (unused argument)

        :returns: whether successful or not
        :rtype: bool
        """
        return (self.redis.publish('handle_delete_file', target_url) > 0)



