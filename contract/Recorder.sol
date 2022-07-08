pragma solidity ^0.5.0;

contract Recorder {
    event InitTaskDone(uint indexed taskID, address indexed who);
    event UpdateTaskDone(uint indexed taskID, address indexed who, uint enrollCount);
    event RecordDone(uint indexed taskID, address indexed who, uint64 indexed layer, uint64 w_or_b, uint128 offset);
    event PrepareGiftDone(uint indexed taskID, uint64 indexed layer, uint64 indexed w_or_b, uint128 offset);

    // 用途: "索引存储"
    struct SliceInfo{
        uint    taskID;
        uint64  layer;
        uint64  w_or_b;
        uint128 offset;
    }
    //  用途: "记录对应索引下的参数"
    struct ParaInfo {
        uint128  factor;
        int128[] para;
    }

    struct Task {
        string taskDesc;
        uint taskID;      // 1 byte = uint8 = 0~256
        uint taskReqNum;  // taskReqNum 从1开始计数, 且数据类型与currentNum保持一致
        uint currentNum;  // byte32这个类型决定了partner数组的大小
        bool status;      // alive or died/0 or 1
        address[] partnerList;

        // 控制字段
        uint128 SNEpoch;
        uint128 SNBatch;
        address SNController;
        address[] SNPresenters;
        uint64[]  layerList;
        uint64[]  typeList;
        uint128[] offsetList;
        //      address ->         Epoch   ->         Batch      ->      layer  ->  w_or_b/type   ->         offset  -> uploaded
        mapping(address => mapping(uint128 => mapping(uint128 => mapping(uint64 => mapping(uint64 => mapping(uint128 => bool)))))) uploaded;
        SliceInfo index;
        //      address ->         layer  ->  w_or_b/type   ->         offset  -> ParaInfo
        mapping(address => mapping(uint64 => mapping(uint64 => mapping(uint128 => ParaInfo)))) recorders;
        //      layer  ->         type   ->         offset  -> giftArray
        mapping(uint64 => mapping(uint64 => mapping(uint128 => int128[]))) allGifts;

    }

    mapping(uint => Task) taskList;

    // 初始化一个新任务
    function initTask(Task storage t, uint id, uint reqNum) private returns (bool){
        t.taskID = id;
        t.taskReqNum = reqNum;
        t.currentNum = 1;
        t.partnerList.push(msg.sender);
        t.status = true;
        return true;
    }

    // 更新任务伙伴信息
    function updateTask(Task storage t) private returns (bool) {
        t.currentNum += 1;
        assert(t.currentNum <= t.taskReqNum);
        t.partnerList.push(msg.sender);
        return true; // return SUC
    }

    // 外部API
    function taskHandler(uint id, uint reqNum) public returns (bool) {
        // TODO: ID生成的讨论
        Task storage t = taskList[id];
        if (t.currentNum == 0) {
            initTask(t, id, reqNum);
            emit InitTaskDone(id, msg.sender);
            return true;
        }

        if (t.status == true) {
            updateTask(t);
            assert(reqNum == t.taskReqNum);
            emit UpdateTaskDone(id, msg.sender, t.currentNum);
            return true;
        }
        else return false;
    }

    // TODO: function killTask() public {}

    function prepareGift(Task storage t, SliceInfo memory s) private returns (bool){
        int128[] storage g = t.allGifts[s.layer][s.w_or_b][s.offset];

        uint len = t.recorders[t.SNController][s.layer][s.w_or_b][s.offset].para.length;

        // 每次准备之前先进行初始化
        g.length = 0;

        for(uint i = 0; i < len; i++) {
            g.push(t.recorders[t.SNPresenters[0]][s.layer][s.w_or_b][s.offset].para[i]);
        }
        delete t.recorders[t.SNPresenters[0]][s.layer][s.w_or_b][s.offset].para;

        for(uint k = 1; k < t.SNPresenters.length; k++) {
            for(uint i = 0; i < len; i++)
                g[i] += t.recorders[t.SNPresenters[k]][s.layer][s.w_or_b][s.offset].para[i];
            // 每一个客户端传来的参数被加后需要被清空
            delete t.recorders[t.SNPresenters[k]][s.layer][s.w_or_b][s.offset];
        }

        for(uint i = 0; i < len; i++) {
            g[i] = g[i]/(int128)(t.SNPresenters.length);
        }

        // TODO: lajihuishou
        return true;
    }


    function updateSNEpochBatch(Task storage t, uint128 epoch, uint128 batch) private {
        // 更新Epoch
        if (t.SNPresenters.length == 0 && epoch > t.SNEpoch) {
            t.SNEpoch = epoch;
            t.SNBatch = batch;
            t.SNController = msg.sender;
        }
        // 在同一个Epoch内更新Batch
        if (t.SNPresenters.length == 0 && epoch == t.SNEpoch &&
            batch > t.SNBatch) {
            t.SNBatch = batch;
            // 在新的一轮迭代开始时 第一个人被选为控制者
            t.SNController = msg.sender;
        }

    }

    // test only
    function updateSNEpochBatch1(Task storage task, uint128 epoch, uint128 batch) private {
        task.SNEpoch = epoch;
        task.SNBatch = batch;
        task.SNController = msg.sender;
    }

    function recordParaInfo(Task storage task, SliceInfo memory sInfo, ParaInfo memory pInfo) private {
        ParaInfo storage temp = task.recorders[msg.sender][sInfo.layer][sInfo.w_or_b][sInfo.offset];
        task.uploaded[msg.sender][task.SNEpoch][task.SNBatch][sInfo.layer][sInfo.w_or_b][sInfo.offset] = true;
        temp.factor = pInfo.factor;
        // TODO: 这里要检查长度
        temp.para = pInfo.para;
    }

    function recordSliceInfo(Task storage task, SliceInfo memory sInfo) private {
        if (msg.sender == task.SNController) {
            task.layerList.push(sInfo.layer);
            task.typeList.push(sInfo.w_or_b);
            task.offsetList.push(sInfo.offset);
        }
    }

    function updateSNPresentStat(Task storage task) private {
        bool exist;
        for (uint i = 0; i< task.SNPresenters.length; i++) {
            if (msg.sender == task.SNPresenters[i]) {exist = true;}
        }
        if (exist == false) {task.SNPresenters.push(msg.sender);}
    }

    function checkValid(Task storage task) private view {
        bool valid;
        for (uint i = 0; i< task.partnerList.length; i++) {
            if (msg.sender == task.partnerList[i]) {valid = true;}
        }
        assert(valid == true);
    }

    // MLNode在callBack中调用的函数, 用于记录本地计算出来的参数以及参数所属的伦次
    function recordPara(uint taskID, uint128 epoch, uint128 batch, uint64 layer,
        uint64 w_or_b, uint128 factor, uint128 offset,
        int128[] memory para) public returns (bool) {

        Task storage t = taskList[taskID];

        assert(t.status == true);

        // "Node already uploaded!"
        assert(t.uploaded[msg.sender][epoch][batch][layer][w_or_b][offset] == false);
        // 检查是否需要更新Epoch Num
        updateSNEpochBatch(t, epoch, batch);

        /* 如果MLNode传来的Epoch小于当前记录的Epoch, 则终止合约, 代表着该节点计算的太慢了
         "Uploading parameters are not belong to Global Epoch/Batch");
         */
        assert(epoch == t.SNEpoch);
        assert(batch == t.SNBatch);

        SliceInfo memory sInfo = SliceInfo(taskID, layer, w_or_b, offset);
        ParaInfo  memory pInfo = ParaInfo(factor, para);

        recordParaInfo(t, sInfo, pInfo);
        checkValid(t);
        updateSNPresentStat(t);
        recordSliceInfo(t, sInfo);

        if (t.SNPresenters.length >= t.taskReqNum) {
            if (prepareGift(t, sInfo) == true) {
                delete t.SNPresenters;
                // TODO: 需要垃圾回收
                emit PrepareGiftDone(taskID, layer, w_or_b, offset);
            }
        } else {
            emit RecordDone(taskID, msg.sender, layer, w_or_b, offset);
        }

        return (true);

    }

    // 当MLNode监听到PrepareGiftDone事件时可调用此方法
    function getGift(uint taskID, uint64 layer, uint64 w_or_b, uint128 offset)
    public view returns (uint, uint, int128[] memory) {
        return (taskList[taskID].SNEpoch, taskList[taskID].SNBatch,
        taskList[taskID].allGifts[layer][w_or_b][offset]);
        //t.allGifts[s.layer][s.w_or_b][s.offset]
    }

    function getTest1(uint taskID, uint64 layer, uint64 w_or_b, uint128 offset)
    public view returns (uint, uint, int128[] memory) {
        return (taskList[taskID].SNEpoch, taskList[taskID].SNBatch,
        taskList[taskID].recorders[msg.sender][layer][w_or_b][offset].para);

    }

    function getTest2()
    public view returns (uint, uint, uint, uint) {
        return (taskList[1].SNEpoch, taskList[1].SNBatch,
        taskList[1].partnerList.length,
        taskList[1].SNPresenters.length);
    }

    function clean() public{
        delete taskList[1].SNPresenters;
    }

}

/*
1,1,1,1,1,1,1,[-80241337, 237499829,-38564152,-58856187, 22570223, 175331999,-83909295, 109190438,-178776160,-23182784]
1,1,1,1,1,1,1,[ 80241337,-237499829, 38564152, 58856187,-22570223,-175331999, 83909295,-109190438, 178776160, 23182784]
1,2
1,1,1,1
*/