"""Device RPC client."""
import requests

class RpcException(Exception):
    """An exception that occurs because of an RPC call."""
    pass

class RpcClient(object):
    def __init__(self, server_url):
        self.server_url = server_url

    def __getattr__(self, key):
        def wrapped_rpc(*args, **kwargs):
            return self._runrpc(key, args, kwargs)
        return wrapped_rpc

    def _runrpc(self, method_name, args_list, kwargs_dict):
        url = self.server_url + "/runrpc"
        payload = {
            "method": method_name,
            "args": args_list,
            "kwargs": kwargs_dict,
        }
        try:
            res = requests.post(url, json=payload)
        except Exception as ex:
            raise RpcException("Could not connect to RPC server.", ex)
        if res.status_code != 200:
            raise RpcException("Rpc server returned code {}".format(res.status_code))
        resj = res.json()
        if "error" in resj:
            raise RpcException(resj["error"])
        return resj["return"]


if __name__ == "__main__":
    """Example usage."""
    rpcclient = RpcClient("http://localhost:9051")
    # rpcclient = RpcClient("http://10.0.0.2:9051")

    print rpcclient.test_prompt()

    if False:
        print rpcclient.echo("ABC", "DEF", x=1, y=2)
        print rpcclient.add(3, 5)
        try:
            print rpcclient.add()
        except RpcException as ex:
            print "EXCEPTION", ex
        try:
            print rpcclient.alwaysfail()
        except RpcException as ex:
            print "EXCEPTION", ex
        print rpcclient.encrypt(3, 5)
