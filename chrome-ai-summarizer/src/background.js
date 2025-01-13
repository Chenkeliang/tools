async function callDeepSeekAPI(content, apiKey) {
    console.log('Calling DeepSeek API with content length:', content.length);
    const API_URL = 'https://api.deepseek.com/v1/chat/completions';

    const prompt = `请分析以下文章内容，并提供：
1. 简要总结（200字以内）
2. 3-5个主要知识点
3. 2-3个核心要点或见解

文章内容：
${content}`;

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`,
                'Accept': 'text/event-stream'
            },
            body: JSON.stringify({
                model: "deepseek-chat",
                messages: [
                    {
                        role: "user",
                        content: prompt
                    }
                ],
                temperature: 0.7,
                stream: true
            })
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error?.message || '请求失败，状态码：' + response.status);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullContent = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') continue;

                    try {
                        const parsed = JSON.parse(data);
                        const content = parsed.choices[0]?.delta?.content || '';
                        fullContent += content;
                    } catch (e) {
                        console.error('Error parsing chunk:', e);
                    }
                }
            }
        }

        return fullContent;
    } catch (error) {
        console.error('API调用错误:', error);
        throw error;
    }
}

// 快速总结功能
async function quickSummarize(tab) {
    try {
        // 获取API Key
        const data = await chrome.storage.local.get(['deepseekApiKey']);
        if (!data.deepseekApiKey) {
            throw new Error('请先设置API Key');
        }

        // 注入content script
        await chrome.scripting.executeScript({
            target: { tabId: tab.id },
            files: ['src/content.js']
        });

        // 获取页面内容
        const contentResponse = await chrome.tabs.sendMessage(tab.id, { action: "getPageContent" });
        if (!contentResponse.success) {
            throw new Error('获取页面内容失败：' + contentResponse.error);
        }

        // 调用API
        const result = await callDeepSeekAPI(contentResponse.content, data.deepseekApiKey);

        // 保存到历史记录
        const timestamp = new Date().toISOString();
        const processedResult = processResult(result);

        chrome.storage.local.get(['summaryHistory'], (data) => {
            const history = data.summaryHistory || [];
            const existingIndex = history.findIndex(item => item.url === tab.url);
            if (existingIndex !== -1) {
                history[existingIndex] = {
                    url: tab.url,
                    title: tab.title,
                    result: processedResult,
                    timestamp
                };
            } else {
                history.unshift({
                    url: tab.url,
                    title: tab.title,
                    result: processedResult,
                    timestamp
                });
                if (history.length > 50) history.pop();
            }
            chrome.storage.local.set({ summaryHistory: history });
        });

        // 显示通知
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: '总结完成',
            message: '文章已经完成总结，请点击扩展图标查看详细内容'
        });

        return { success: true, result };
    } catch (error) {
        console.error('快速总结错误:', error);
        chrome.notifications.create({
            type: 'basic',
            iconUrl: 'icons/icon128.png',
            title: '总结失败',
            message: error.message
        });
        return { success: false, error: error.message };
    }
}

// 处理总结结果
function processResult(result) {
    const sections = result.split('\n\n');
    let summary = '', keyPoints = '', highlights = '';

    sections.forEach(section => {
        if (section.includes('简要总结')) {
            summary = section.replace(/简要总结[：:]\s*/, '');
        } else if (section.includes('主要知识点')) {
            keyPoints = section.replace(/主要知识点[：:]\s*/, '');
        } else if (section.includes('核心要点')) {
            highlights = section.replace(/核心要点[：:]\s*/, '');
        }
    });

    return { summary, keyPoints, highlights };
}

// 监听快捷键
chrome.commands.onCommand.addListener((command) => {
    if (command === 'quick_summarize') {
        chrome.tabs.query({ active: true, currentWindow: true }, ([tab]) => {
            if (tab) {
                quickSummarize(tab);
            }
        });
    }
});

// 监听来自popup的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Background received message:', request);

    if (request.action === "summarize") {
        (async () => {
            try {
                const result = await callDeepSeekAPI(request.content, request.apiKey);
                sendResponse({ success: true, result });
            } catch (error) {
                console.error('Summary error:', error);
                sendResponse({ success: false, error: error.message });
            }
        })();
        return true; // 保持消息通道开放
    }
}); 