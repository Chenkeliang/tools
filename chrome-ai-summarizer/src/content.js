function extractMainContent() {
    // 尝试获取文章主要内容
    const article = document.querySelector('article') ||
        document.querySelector('.article') ||
        document.querySelector('.post-content') ||
        document.querySelector('.entry-content');

    if (article) {
        return article.innerText;
    }

    // 如果没有明确的文章标记，尝试智能提取主要内容
    const mainContent = document.querySelector('main') || document.querySelector('#main');
    if (mainContent) {
        return mainContent.innerText;
    }

    // 回退方案：提取所有段落文本
    const paragraphs = Array.from(document.querySelectorAll('p'))
        .filter(p => p.innerText.length > 100) // 过滤掉太短的段落
        .map(p => p.innerText)
        .join('\n\n');

    return paragraphs || document.body.innerText;
}

// 监听来自popup或background的消息
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    console.log('Content script received message:', request);

    if (request.action === "getPageContent") {
        try {
            const content = extractMainContent();
            console.log('Extracted content length:', content.length);
            sendResponse({ success: true, content: content });
        } catch (error) {
            console.error('Error extracting content:', error);
            sendResponse({ success: false, error: error.message });
        }
    }
    return true; // 保持消息通道开放
}); 