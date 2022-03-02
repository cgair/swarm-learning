pragma solidity ^0.5.0;
// TODO: 如何让不符合条件的入参直接返回而不执行更多的命令? event函数实现

contract TaskHandler {
    struct Task {
        string taskDesc;
        uint taskID;      // 1 byte = uint8 = 0~256
        uint taskReqNum;  // taskReqNum 从1开始计数, 且数据类型与currentNum保持一致
        uint currentNum;  // byte32这个类型决定了partner数组的大小
        bool status;      // alive or died/0 or 1
    }
    // 用来索引所有的TASK TODO: 是否要用两个表来保存活的和死得taskID
    mapping(uint => Task) private taskDict;
    // 用来保存TASKID
    mapping(uint => bool) private taskIDList;

    function genTaskID(string memory desc) private returns (uint) {
        return uint(sha256(bytes(desc)));
    }

    // 初始化一个新任务
    function initTask(string memory taskDesc, uint reqNum) private returns (bool){
        Task memory task;

        task.taskDesc = taskDesc;
        task.taskID = genTaskID(task.taskDesc);
        task.taskReqNum = reqNum;
        task.currentNum = 1;
        task.status = true;
        taskDict[task.taskID] = task;  //TODO: 这里是需要验证的
        return true;
    }

    // 更新任务伙伴信息
    function updateTask(uint taskID) private returns (bool) {
        taskDict[taskID].currentNum += 1;
        return true; // return SUC
    }

    //TODO:  任务执行完成时标记任务终止 需要安全特性 防止taskID复活
    function killTask(uint taskID) public returns (bool) {
        taskDict[taskID].status = false;
        return true; // return SUC
    }

    // 外部API
    function taskHandler(string memory desc, uint reqNum) public returns (bool) {
        uint id = genTaskID(desc);
        // TODO: project:/contracts/TaskHandler.sol:47:13: TypeError: Operator == not compatible with types struct TaskHandler.Task storage ref and int_const 0
        // if (taskDict[id] == 0) {
        if (taskIDList[id] == false) {
            initTask(desc, reqNum);
            taskIDList[id] == true;
            // TODO: hurry! log function
            return true;
        }
        else if (taskDict[id].status == true) {
            updateTask(id);
            return true;
        }
        else return false;
    }

}
