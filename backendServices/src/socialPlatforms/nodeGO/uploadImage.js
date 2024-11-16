const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

// 通过命令行参数获取传递的参数
const [,, note_id, cookie, useragent, filePath, proxies] = process.argv;

async function postImage() {
    const url = "https://note.com/api/v1/image_upload/note_eyecatch";

    // 创建 form-data 实例
    const form = new FormData();

    // 确保文件路径存在并且是二进制文件
    if (fs.existsSync(filePath)) {
        form.append('file', fs.createReadStream(filePath)); // 使用 fs.createReadStream 读取文件
    } else {
        console.error(`File not found: ${filePath}`);
        return;
    }

    // 添加其它表单数据
    form.append('note_id', note_id);   // note_id
    form.append('width', 1920);         // 宽度
    form.append('height', 1005);        // 高度

    // 设置请求头
    const headers = {
        'cookie': cookie,
        'referer': 'https://editor.note.com/',
        'user-agent': useragent,
        'x-requested-with': 'XMLHttpRequest',
        ...form.getHeaders() // 合并 form-data 的 headers
    };

    // 配置代理（如果有）
    const axiosConfig = proxies ? {
        headers: headers,
        proxy: {
            host: proxies.split(':')[0].trim().replace(/"/g, ''), // 获取代理的 IP
            port: parseInt(proxies.split(':')[1]) // 获取代理的端口
        },
        timeout: 10000 // 增加超时时间（毫秒）
    } : {
        headers: headers,
        timeout: 10000
    };

    // 打印代理设置，确保它的格式正确
    if (axiosConfig.proxy) {
        console.log("Using proxy:", axiosConfig.proxy);
    } else {
        console.log("No proxy configured.");
    }

    try {
        // 发送 POST 请求上传图片
        const response = await axios.post(url, form, axiosConfig);
        console.log("Image uploaded successfully:", response.data);
    } catch (error) {
        console.error("Error uploading image:", error.message);
    }
}

postImage();
