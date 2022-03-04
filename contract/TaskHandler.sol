pragma solidity ^0.5.0;
// TODO: 如何让不符合条件的入参直接返回而不执行更多的命令? event函数实现

contract TaskHandler {
    event InitTaskDone();
    event UpdateTaskDone();

    struct Task {
        string taskDesc;
        uint taskID;      // 1 byte = uint8 = 0~256
        uint taskReqNum;  // taskReqNum 从1开始计数, 且数据类型与currentNum保持一致
        uint currentNum;  // byte32这个类型决定了partner数组的大小
        address[] partnerList;
        bool status;      // alive or died/0 or 1
    }
    mapping(uint => Task) taskList;

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
        taskList[taskID].partnerList.push(msg.sender);
        return true; // return SUC
    }

    // 外部API
    function taskHandler(uint id, uint reqNum) public returns (bool) {

        // TODO: project:/contracts/TaskHandler.sol:47:13: TypeError: Operator == not compatible with types struct TaskHandler.Task storage ref and int_const 0
        // TODO: !!!
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

}