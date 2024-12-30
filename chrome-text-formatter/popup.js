document.addEventListener('DOMContentLoaded', function () {
    const inputText = document.getElementById('input');
    const formatType = document.getElementById('format-type');
    const formatButton = document.getElementById('format');
    const copyButton = document.getElementById('copy');
    const output = document.getElementById('output');
    const shortcutHint = document.querySelector('.shortcut-hint');

    // 检测操作系统，更新快捷键提示
    const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
    shortcutHint.textContent = isMac ? '⌘ + ⏎' : 'Ctrl + ⏎';

    // 自动调整文本框高度
    function adjustTextareaHeight() {
        this.style.height = 'auto';
        const newHeight = Math.min(Math.max(this.scrollHeight, 120), 300);
        this.style.height = newHeight + 'px';
    }

    inputText.addEventListener('input', adjustTextareaHeight);

    // 添加输入动画效果
    inputText.addEventListener('focus', function () {
        this.parentElement.style.transform = 'scale(1.005)';
        this.parentElement.style.transition = 'transform 0.2s ease';
    });

    inputText.addEventListener('blur', function () {
        this.parentElement.style.transform = 'scale(1)';
    });

    function cleanItem(item) {
        // 移除所有引号、逗号和多余的空白
        let cleaned = item.trim().replace(/["\',]+$/, ''); // 移除尾部的引号和逗号
        cleaned = cleaned.replace(/^["']/, ''); // 移除开头的引号
        cleaned = cleaned.replace(/["']$/, ''); // 移除结尾的引号
        return cleaned.trim();
    }

    function formatText(text, formatType) {
        try {
            if (!text.trim()) {
                return '';
            }

            // 移除空行和首尾空白，同时处理可能的特殊字符
            text = text.replace(/\r/g, '').trim();

            // 分割行，并清理每一行
            let lines = text.split('\n').filter(line => line.trim());

            // 处理混合分隔符的情况（逗号和空格）
            let items = [];
            if (lines.length === 1) {
                // 使用正则表达式处理可能的特殊分隔符
                items = lines[0].split(/[,\s]+/).filter(item => item.trim());
            } else {
                items = lines;
            }

            // 清理每一项
            items = items.map(cleanItem).filter(item => item);

            if (items.length === 0) {
                return '';
            }

            // 根据format_type选择不同的格式化方式
            switch (formatType) {
                case '1': // 横排带引号
                    return `"${items.join('","')}"`;
                case '2': // 竖排不带引号
                    return items.join(',\n');
                case '3': // 竖排不带引号和逗号
                    return items.join('\n');
                default: // 默认：竖排带引号
                    return items.map(item => `"${item}"`).join(',\n');
            }
        } catch (e) {
            console.error('处理文本时出错:', e);
            return '处理文本时发生错误，请检查输入格式';
        }
    }

    // 添加按钮点击效果
    function addButtonClickEffect(button) {
        button.addEventListener('mousedown', function () {
            this.style.transform = 'scale(0.97) translateY(1px)';
        });

        button.addEventListener('mouseup', function () {
            this.style.transform = 'scale(1) translateY(0)';
        });

        button.addEventListener('mouseleave', function () {
            this.style.transform = 'scale(1) translateY(0)';
        });
    }

    addButtonClickEffect(formatButton);
    addButtonClickEffect(copyButton);

    formatButton.addEventListener('click', function () {
        const text = inputText.value;
        const type = formatType.value;
        const result = formatText(text, type);

        if (!result) {
            output.innerHTML = '<span class="empty-result">请输入需要格式化的文本</span>';
            copyButton.disabled = true;
            copyButton.style.opacity = '0.5';
        } else {
            output.textContent = result;
            copyButton.disabled = false;
            copyButton.style.opacity = '1';
            // 添加结果显示动画
            output.style.opacity = '0';
            output.style.transform = 'translateY(6px)';
            output.style.transition = 'all 0.2s ease';
            requestAnimationFrame(() => {
                output.style.opacity = '1';
                output.style.transform = 'translateY(0)';
            });
        }
    });

    copyButton.addEventListener('click', function () {
        if (this.disabled) return;

        const result = output.textContent;
        if (result && !output.querySelector('.empty-result')) {
            navigator.clipboard.writeText(result).then(() => {
                copyButton.textContent = '已复制';
                copyButton.classList.add('success');
                // 添加复制成功动画
                copyButton.style.transform = 'scale(1.02)';
                setTimeout(() => {
                    copyButton.style.transform = 'scale(1)';
                    copyButton.textContent = '复制';
                    copyButton.classList.remove('success');
                }, 1500);
            }).catch(err => {
                console.error('复制失败:', err);
                copyButton.textContent = '复制失败';
                setTimeout(() => {
                    copyButton.textContent = '复制';
                }, 1500);
            });
        }
    });

    // 添加键盘快捷键支持
    document.addEventListener('keydown', function (e) {
        // Ctrl/Cmd + Enter 触发格式化
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            formatButton.click();
            // 添加快捷键反馈
            formatButton.style.transform = 'scale(0.95)';
            setTimeout(() => {
                formatButton.style.transform = 'scale(1)';
            }, 100);
        }
        // Ctrl/Cmd + Shift + C 触发复制
        if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'C') {
            e.preventDefault();
            if (!copyButton.disabled) {
                copyButton.click();
            }
        }
    });

    // 初始化时自动聚焦到输入框
    inputText.focus();

    // 初始化时禁用复制按钮
    copyButton.disabled = true;
    copyButton.style.opacity = '0.5';
}); 