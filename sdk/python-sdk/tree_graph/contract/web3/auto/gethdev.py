from tree_graph.contract.web3 import  (
    IPCProvider,
    Web3,
)
from tree_graph.contract.web3 .middleware import (
    geth_poa_middleware,
)
from tree_graph.contract.web3 .providers.ipc import (
    get_dev_ipc_path,
)

w3 = Web3(IPCProvider(get_dev_ipc_path()))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
