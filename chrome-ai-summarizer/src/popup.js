document.addEventListener('DOMContentLoaded', () => {
    const apiKeyInput = document.getElementById('apiKeyInput');
    const saveApiKeyBtn = document.getElementById('saveApiKey');
    const summarizeBtn = document.getElementById('summarize');
    const loadingDiv = document.querySelector('.loading');
    const resultDiv = document.querySelector('.result');
    const summaryDiv = document.getElementById('summary');
    const keyPointsDiv = document.getElementById('keyPoints');
    const highlightsDiv = document.getElementById('highlights');
    const exportBtn = document.getElementById('exportBtn');
    const showHistoryBtn = document.getElementById('showHistoryBtn');
    const historyList = document.getElementById('historyList');
    const historyItems = document.querySelector('.history-items');
    const backToHistoryBtn = document.getElementById('backToHistory');
    const clearHistoryBtn = document.getElementById('clearHistory');
    const exportAllHistoryBtn = document.getElementById('exportAllHistory');
    const tabs = document.querySelectorAll('.tab');
    const tabContents = document.querySelectorAll('.tab-content');

    console.log('Popup script loaded');

    // 标签页切换逻辑
    function switchTab(tabId) {
        // 移除所有活动状态
        tabs.forEach(tab => tab.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));

        // 激活选中的标签页
        const selectedTab = document.querySelector(`[data-tab="${tabId}"]`);
        const selectedContent = document.getElementById(`${tabId}Tab`);
        selectedTab.classList.add('active');
        selectedContent.classList.add('active');

        // 如果切换到历史记录标签，自动加载历史记录
        if (tabId === 'history') {
            displayHistory();
        }
    }

    // 为标签页添加点击事件
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const tabId = tab.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    // 配置 Marked 选项
    marked.setOptions({
        breaks: true,
        gfm: true,
        headerIds: false,
        mangle: false
    });

    // 加载保存的API Key
    chrome.storage.local.get(['deepseekApiKey'], (result) => {
        console.log('Loaded API key:', result.deepseekApiKey ? '已设置' : '未设置');
        if (result.deepseekApiKey) {
            apiKeyInput.value = result.deepseekApiKey;
        }
    });

    // 保存API Key
    saveApiKeyBtn.addEventListener('click', () => {
        const apiKey = apiKeyInput.value.trim();
        if (apiKey) {
            chrome.storage.local.set({ deepseekApiKey: apiKey }, () => {
                console.log('API key saved');
                alert('API Key已保存');
            });
        } else {
            alert('请输入有效的API Key');
        }
    });

    // 处理总结结果
    function processResult(result) {
        console.log('Processing result:', result);
        const sections = result.split('\n\n');
        let summary = '', keyPoints = '', highlights = '';

        sections.forEach(section => {
            if (section.includes('简要总结')) {
                summary = section.replace(/简要总结[：:]\s*/, '');
            } else if (section.includes('主要知识点')) {
                keyPoints = section.replace(/主要知识点[：:]\s*/, '');
                // 转换为Markdown列表格式
                keyPoints = keyPoints.split(/\d+\.\s*/).filter(Boolean)
                    .map(point => `- ${point.trim()}`).join('\n');
            } else if (section.includes('核心要点')) {
                highlights = section.replace(/核心要点[：:]\s*/, '');
                // 转换为Markdown列表格式
                highlights = highlights.split(/\d+\.\s*/).filter(Boolean)
                    .map(point => `- ${point.trim()}`).join('\n');
            }
        });

        // 使用Markdown渲染
        summaryDiv.innerHTML = marked.parse(summary);
        keyPointsDiv.innerHTML = marked.parse(keyPoints);
        highlightsDiv.innerHTML = marked.parse(highlights);

        return { summary, keyPoints, highlights };
    }

    // 保存到历史记录
    async function saveToHistory(url, title, result) {
        console.log('Saving to history:', { url, title });
        const timestamp = new Date().toISOString();
        const historyItem = {
            url,
            title,
            result,
            timestamp
        };

        chrome.storage.local.get(['summaryHistory'], (data) => {
            const history = data.summaryHistory || [];
            // 检查是否已存在相同URL的记录
            const existingIndex = history.findIndex(item => item.url === url);
            if (existingIndex !== -1) {
                // 更新现有记录
                history[existingIndex] = historyItem;
            } else {
                // 添加新记录
                history.unshift(historyItem);
                // 只保留最近50条记录
                if (history.length > 50) history.pop();
            }
            chrome.storage.local.set({ summaryHistory: history });
        });
    }

    // 显示历史记录
    function displayHistory() {
        console.log('Displaying history');
        chrome.storage.local.get(['summaryHistory'], (data) => {
            const history = data.summaryHistory || [];
            const historyItems = document.querySelector('.history-items');
            historyItems.innerHTML = '';

            if (history.length === 0) {
                historyItems.innerHTML = '<div class="no-history">暂无历史记录</div>';
            } else {
                history.forEach(item => {
                    const div = document.createElement('div');
                    div.className = 'history-item';
                    div.innerHTML = `
                        <div class="history-meta">
                            <div class="history-title">${item.title}</div>
                            <div class="history-date">${new Date(item.timestamp).toLocaleString()}</div>
                        </div>
                        <div class="history-url">${item.url}</div>
                        <div class="history-preview">${item.result.summary.slice(0, 100)}...</div>
                    `;
                    div.addEventListener('click', () => {
                        summaryDiv.innerHTML = marked.parse(item.result.summary);
                        keyPointsDiv.innerHTML = marked.parse(item.result.keyPoints);
                        highlightsDiv.innerHTML = marked.parse(item.result.highlights);
                        switchTab('summarize');
                        resultDiv.style.display = 'block';
                    });
                    historyItems.appendChild(div);
                });
            }
        });
    }

    // 导出单个结果
    function exportResult() {
        console.log('Exporting result');
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            const content = `# AI文章总结 - ${tabs[0].title}

URL: ${tabs[0].url}
时间: ${new Date().toLocaleString()}

## 📝 内容总结
${summaryDiv.textContent}

## 🔑 主要知识点
${keyPointsDiv.textContent}

## 💡 核心要点
${highlightsDiv.textContent}
`;

            const blob = new Blob([content], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const filename = `summary_${new Date().toISOString().slice(0, 10)}.md`;

            chrome.downloads.download({
                url: url,
                filename: filename,
                saveAs: true
            });
        });
    }

    // 导出所有历史记录
    function exportAllHistory() {
        chrome.storage.local.get(['summaryHistory'], (data) => {
            const history = data.summaryHistory || [];
            if (history.length === 0) {
                alert('暂无历史记录可导出');
                return;
            }

            const content = history.map(item => `# AI文章总结 - ${item.title}

URL: ${item.url}
时间: ${new Date(item.timestamp).toLocaleString()}

## 📝 内容总结
${item.result.summary}

## 🔑 主要知识点
${item.result.keyPoints}

## 💡 核心要点
${item.result.highlights}

---
`).join('\n\n');

            const blob = new Blob([content], { type: 'text/markdown' });
            const url = URL.createObjectURL(blob);
            const filename = `all_summaries_${new Date().toISOString().slice(0, 10)}.md`;

            chrome.downloads.download({
                url: url,
                filename: filename,
                saveAs: true
            });
        });
    }

    // 清空历史记录
    function clearHistory() {
        if (confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
            chrome.storage.local.set({ summaryHistory: [] }, () => {
                displayHistory();
            });
        }
    }

    // 总结按钮点击事件
    summarizeBtn.addEventListener('click', async () => {
        console.log('Summarize button clicked');
        const apiKey = apiKeyInput.value.trim();
        if (!apiKey) {
            alert('请先输入API Key');
            return;
        }

        loadingDiv.style.display = 'block';
        resultDiv.style.display = 'none';

        try {
            // 获取当前标签页
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            console.log('Current tab:', tab.url);

            // 注入content script
            await chrome.scripting.executeScript({
                target: { tabId: tab.id },
                files: ['src/content.js']
            });

            // 从content script获取页面内容
            const contentResponse = await chrome.tabs.sendMessage(tab.id, { action: "getPageContent" });
            console.log('Content response:', contentResponse);

            if (!contentResponse.success) {
                throw new Error('获取页面内容失败：' + contentResponse.error);
            }

            // 调用background script进行API请求
            const response = await chrome.runtime.sendMessage({
                action: "summarize",
                content: contentResponse.content,
                apiKey: apiKey
            });

            console.log('API response:', response);
            loadingDiv.style.display = 'none';

            if (response.success) {
                resultDiv.style.display = 'block';
                const processedResult = processResult(response.result);
                // 保存到历史记录
                await saveToHistory(tab.url, tab.title, processedResult);
                // 如果在历史记录标签页，刷新显示
                if (document.querySelector('[data-tab="history"]').classList.contains('active')) {
                    displayHistory();
                }
            } else {
                throw new Error(response.error);
            }
        } catch (error) {
            console.error('Error during summarization:', error);
            loadingDiv.style.display = 'none';
            alert('发生错误: ' + error.message);
        }
    });

    // 导出按钮事件
    exportBtn.addEventListener('click', exportResult);

    // 清空历史记录按钮事件
    clearHistoryBtn.addEventListener('click', () => {
        if (confirm('确定要清空所有历史记录吗？此操作不可恢复。')) {
            chrome.storage.local.set({ summaryHistory: [] }, () => {
                displayHistory();
            });
        }
    });

    // 导出所有历史记录按钮事件
    exportAllHistoryBtn.addEventListener('click', exportAllHistory);

    // 初始加载历史记录
    if (document.querySelector('[data-tab="history"]').classList.contains('active')) {
        displayHistory();
    }
}); 