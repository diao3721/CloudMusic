function urlencode (data){
    var _result = [];
    for (var key in data){
        var value = data[key];
        if (value.constructor == Array){
            value.forEach(function(_value){
                _result.push(key + "=" + _value);
            });
        }else{
            _result.push(key + '=' + value);
        }
    }

    return _result.join('&');
}
//对象排序
function sortObj(sortObj) {
    var arr = [];
    for (var ji in sortObj) {
        arr.push([sortObj[ji],ji]);
    }
    arr.sort(function (a,b) {
        return a[0] - b[0];
    });
    var len = arr.length,
        obj = {};
    for (var pi = 0; pi < len; pi++) {
        obj[arr[pi][1]] = arr[pi][0];
    }
    return obj;
}
/**
 * 将秒转换为 分:秒
 * s int 秒数
*/
function s_to_hs(s){
    //计算分钟
    //算法：将秒数除以60，然后下舍入，既得到分钟数
    var h;
    h  =   Math.floor(s/60);
    //计算秒
    //算法：取得秒%60的余数，既得到秒数
    s  =   s%60;
    //将变量转换为字符串
    h    +=    '';
    s    +=    '';
    //如果只有一位数，前面增加一个0
    h  =   (h.length==1)?'0'+h:h;
    s  =   (s.length==1)?'0'+s:s;
    return h+':'+s;
}

/**
 * 将毫秒转化成分钟
 * @param mss
 * @returns {string}
 */
function ms_to_hs(mss) {
    var minutes = parseInt((mss % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = Math.round((mss % (1000 * 60)) / 1000);
    return minutes + ":" + seconds ;
}

/**
 * 获取演唱者
 * @param obj
 */
function getSinger(obj){
    // console.log(obj);
    // console.log(typeof obj);
    // console.log(obj[0].name);
    // console.log(obj.shift().name);
    return obj[0].name;
}
//判断字符是否为空的方法
function isEmpty(obj){
	if(typeof obj == "undefined" || obj == null || obj == ""){
		return true;
	}else{
		return false;
	}
}