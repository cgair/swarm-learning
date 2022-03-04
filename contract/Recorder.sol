pragma solidity ^0.5.0;

contract Recorder {
    event InitTaskDone();
    event UpdateTaskDone();
    event RecordDone(address from);
    event prepareGiftDone();

    struct Task {
        string taskDesc;
        uint taskID;      // 1 byte = uint8 = 0~256
        uint taskReqNum;  // taskReqNum 从1开始计数, 且数据类型与currentNum保持一致
        uint currentNum;  // byte32这个类型决定了partner数组的大小
        address[] partnerList;
        bool status;      // alive or died/0 or 1
    }
    mapping(uint => Task) taskList;

    // 用于存储参数 TODO: NestedMapping
    // 控制字段
    uint SNEpoch = 0;
    uint SNBatch = 0;
    address SNController;
    address[] SNPresenterList;
    uint64[]  layerList;
    uint64[]  typeList;
    uint128[] offsetList;

    struct relatedPara {
        uint128  factor;
        bool     uploaded;
        int128[] para;
    }
    //      address ->         layer  ->  w_or_b/type   ->         offset  -> relatedPara
    mapping(address => mapping(uint64 => mapping(uint64 => mapping(uint128 => relatedPara)))) recorder;

    // layer -> type -> offset -> gift
    mapping(uint64 => mapping(uint64 => mapping(uint128 => int128[]))) allGifts;

    // 初始化一个新任务
    function initTask(uint id, uint reqNum) private returns (bool){
        taskList[id].taskID = id;
        taskList[id].taskReqNum = reqNum;
        taskList[id].currentNum = 1;
        taskList[id].partnerList.push(msg.sender);
        taskList[id].status = true;

        return true;
    }

    // 更新任务伙伴信息
    function updateTask(uint taskID) private returns (bool) {
        taskList[taskID].currentNum += 1;
        assert(taskList[taskID].currentNum <= taskList[taskID].taskReqNum);
        taskList[taskID].partnerList.push(msg.sender);
        return true; // return SUC
    }

    // 外部API
    function taskHandler(uint id, uint reqNum) public returns (bool) {
        // TODO: ID生成的讨论
        if (taskList[id].currentNum == 0) {
            initTask(id, reqNum);
            // TODO: hurry! log function
            emit InitTaskDone();
            return true;
        }

        if (taskList[id].status == true) {
            updateTask(id);
            emit UpdateTaskDone();
            return true;
        }
        else return false;
    }

    // TODO: function killTask() public {}

    function prepareGift(uint64 layer, uint64 w_or_b, uint128 offset) private returns (bool){
        uint len = recorder[SNController][layer][w_or_b][offset].para.length;
        // 每次准备之前先进行初始化
        delete allGifts[layer][w_or_b][offset];
        for(uint i = 0; i < len; i++) {
            allGifts[layer][w_or_b][offset].push(recorder[SNPresenterList[0]][layer][w_or_b][offset].para[i]);
        }
        delete recorder[SNPresenterList[0]][layer][w_or_b][offset];

        for(uint k = 1; k < SNPresenterList.length; k++) {
            for(uint i = 0; i < len; i++)
                allGifts[layer][w_or_b][offset][i] += recorder[SNPresenterList[k]][layer][w_or_b][offset].para[i];
            // 每一个客户端传来的参数被加后需要被清空
            delete recorder[SNPresenterList[k]][layer][w_or_b][offset];
        }
        return true;
    }
    
    function updateSNEpochBatch(uint epoch, uint batch) private {
        // 更新Epoch
        if (SNPresenterList.length == 0 && epoch > SNEpoch) {
            SNEpoch = epoch;
            SNBatch = batch;
            SNController = msg.sender;
        }
        // 在同一个Epoch内更新Batch
        if (SNPresenterList.length == 0 && epoch == SNEpoch && batch > SNBatch) {
            SNBatch = batch;
            // 在新的一轮迭代开始时 第一个人被选为控制者
            SNController = msg.sender;
        }
    }

    function updateRelatedPara(address partner, uint64 layer, uint64 w_or_b,
        uint128 factor, uint128 offset, int128[] memory para) private {
        recorder[partner][layer][w_or_b][offset].factor = factor;
        recorder[partner][layer][w_or_b][offset].uploaded = true;
        recorder[partner][layer][w_or_b][offset].para = para;
    }

    function updateSliceInfo(address partner, uint64 layer, uint64 w_or_b, uint128 offset) private {
        if (partner == SNController) {
            layerList.push(layer);
            typeList.push(w_or_b);
            offsetList.push(offset);
        }
    }

    function updateSNPresentStat(address partner) private {
        bool exist;
        for (uint i = 0; i< SNPresenterList.length; i++) {
            if (partner == SNPresenterList[i]) {exist = true;}
        }
        if (exist == false) {SNPresenterList.push(partner);}
    }

    function checkVaild(address partner, uint id) private view {
        bool valid;
        for (uint i = 0; i< taskList[id].partnerList.length; i++) {
            if (partner == taskList[id].partnerList[i]) {valid = true;}
        }
        assert(valid == true);
    }

    // MLNode在callBack中调用的函数, 用于记录本地计算出来的参数以及参数所属的伦次
    function recordPara(uint taskID, uint128 epoch, uint128 batch, uint64 layer,
        uint64 w_or_b, uint128 factor, uint128 offset,
        int128[] memory para) public returns (bool) {
        assert(taskList[taskID].status == true);
        // "Node already uploaded!"
        assert(recorder[msg.sender][layer][w_or_b][offset].uploaded == false);
        // 检查是否需要更新Epoch Numb
        updateSNEpochBatch(epoch, batch);
        // 如果MLNode传来的Epoch小于当前记录的Epoch, 则终止合约, 代表着该节点计算的太慢了
        // "Uploading parameters are not belong to Global Epoch/Batch");
        assert(epoch == SNEpoch);
        assert(batch == SNBatch);
        updateRelatedPara(msg.sender, layer, w_or_b, factor, offset, para);
        checkVaild(msg.sender, taskID);
        updateSNPresentStat(msg.sender);
        updateSliceInfo(msg.sender, layer, w_or_b, offset);

        if (SNPresenterList.length >= taskList[taskID].taskReqNum) {
            if (prepareGift(layer, w_or_b, offset) == true) {
                delete SNPresenterList;
                emit prepareGiftDone();
            }
        } else {
            emit RecordDone(msg.sender);
        }

        return (true);

    }

    // 当MLNode监听到prepareGiftDone事件时可调用此方法
    function getGift(uint64 layer, uint64 w_or_b, uint128 offset) public view returns (uint, uint, int128[] memory) {
        return (SNEpoch, SNBatch, allGifts[layer][w_or_b][offset]);
    }

    function gettest() public view returns (uint, uint, uint) {
        return (SNEpoch, SNBatch, taskList[1].partnerList.length);
    }

}

/*
1,1,1,1,1,1,1,[1,2,3,4]
1,2
1,1,1
*/