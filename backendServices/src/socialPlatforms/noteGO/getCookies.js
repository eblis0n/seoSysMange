const axios = require('axios');
const puppeteer = require('puppeteer-core');

const ads_api = process.argv[2];
const user_id = process.argv[3];

const main = async () => {
    let res;
    try {
        res = await axios.get(`${ads_api}/api/v1/browser/start?user_id=${user_id}`);
    } catch (error) {
        console.error("Failed to fetch browser WS endpoint:", error);
        process.exit(1);
    }

    if (!(res.data.code === 0 && res.data.data.ws && res.data.data.ws.puppeteer)) {
        console.error("Invalid response structure or missing WS endpoint.");
        process.exit(1);
    }

    let browser;
    try {
        browser = await puppeteer.connect({
            browserWSEndpoint: res.data.data.ws.puppeteer,
            defaultViewport: null
        });
    } catch (error) {
        console.error("Failed to connect to Puppeteer browser:", error);
        process.exit(1);
    }

    try {
        const page = await browser.newPage();
        await page.setRequestInterception(true);

        page.on('request', interceptedRequest => {
            const url = interceptedRequest.url();
            if (url.includes('https://note.com/api/v2/current_user')) {
                const headers = interceptedRequest.headers();
                if (headers['cookie']) {
                    const cookiedata = {
                        "user_id": `${user_id}`,
                        "cookie": headers['cookie'],
                        "user-agent": headers['user-agent']
                    };
                    console.log(JSON.stringify(cookiedata));
                }
            }
            interceptedRequest.continue().catch(err => {
                console.error("Request continuation failed:", err);
            });
        });

        await page.goto(`https://editor.note.com/new`, { waitUntil: 'networkidle0', timeout: 30000 });
        await page.close();
    } catch (error) {
        console.error("Error during Puppeteer operations:", error);
    } finally {
        if (browser) {
            await browser.close().catch(err => {
                console.error("Failed to close browser:", err);
            });
        }
        // console.log("Exiting script...");
    }
};

main();
