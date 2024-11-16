const axios = require('axios');
const puppeteer = require('puppeteer-core');
// const fs = require('fs');

// 获取命令行参数
const ads_api = process.argv[2];
const user_id = process.argv[3];
// const filepath = process.argv[4];

// 等待的辅助函数
// function wait(ms) {
//     return new Promise(resolve => setTimeout(() => resolve(), ms));
// };

// 文件写入函数
// const writeOutput = (file, data) => {
//     fs.appendFile(file, data, function (err) {
//         if (err) throw err;
//     });
// }

const main = async () => {
    let res = await axios.get(`${ads_api}/api/v1/browser/start?user_id=${user_id}`);
    console.log('Response:', res.data); // 打印响应信息

    if (!(res.data.code === 0 && res.data.data.ws && res.data.data.ws.puppeteer)) {
        return false;
    }

    try {
        const browser = await puppeteer.connect({
            browserWSEndpoint: res.data.data.ws.puppeteer,
            defaultViewport: null
        });

        const page = await browser.newPage();
        await page.setRequestInterception(true);

        page.on('request', interceptedRequest => {
            const url = interceptedRequest.url();
            if (url.includes('https://note.com/api/v2/current_user')) {
                const headers = interceptedRequest.headers();
                // console.log('Request Headers:', headers); // 打印请求头

                if (headers['cookie']) {
                    const cookiedata = {
                        "user_id": `${user_id}`,
                        "cookie": headers['cookie'],
                        "user-agent": headers['user-agent']
                    };
                    // writeOutput(filepath, JSON.stringify(cookiedata) + '\n');
                    console.log(JSON.stringify(cookiedata)); // 打印请求头
                }
                interceptedRequest.continue();
            } else {
                interceptedRequest.continue();
            }
        });

        // await page.goto(`https://editor.note.com/new`, { waitUntil: 'networkidle0' });
        await page.goto(`https://editor.note.com/new`, { waitUntil: 'networkidle0', timeout: 100000 });
        await page.close();
        await browser.close();
    } catch (e) {
        console.error(e);
    }finally {
        console.log('Exiting script...');
        process.exit(0); // 确保退出程序，0 表示正常退出
    }
}

main();
