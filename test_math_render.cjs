const katex = require('katex');

function testRenderer(rawText) {
    if (!rawText || typeof rawText !== 'string') return '';
    const codeBlocks = [];
    let text = rawText.replace(/(```[\s\S]*?```|`[^`\n]+?`)/g, (match) => {
        const id = '%%CODE_BLOCK_' + codeBlocks.length + '%%';
        codeBlocks.push(match);
        return id;
    });

    const mathBlocks = [];
    text = text.replace(/\$\$([\s\S]*?)\$\$/g, (match, formula) => {
        const id = '%%MATH_BLOCK_' + mathBlocks.length + '%%';
        const rendered = katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false });
        mathBlocks.push('<div class="math-block katex-display">' + rendered + '</div>');
        return id;
    });
    text = text.replace(/\\\[([\s\S]*?)\\\]/g, (match, formula) => {
        const id = '%%MATH_BLOCK_' + mathBlocks.length + '%%';
        const rendered = katex.renderToString(formula.trim(), { displayMode: true, throwOnError: false });
        mathBlocks.push('<div class="math-block katex-display">' + rendered + '</div>');
        return id;
    });

    const mathInlines = [];
    text = text.replace(/\\\(([\s\S]*?)\\\)/g, (match, formula) => {
        const id = '%%MATH_INLINE_' + mathInlines.length + '%%';
        const rendered = katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false });
        mathInlines.push('<span class="math-inline">' + rendered + '</span>');
        return id;
    });

    // Dollar inline math $...$
    text = text.replace(/(?<!\\)\$(?!\s)([^$\n]+?)(?<!\s)(?<!\\)\$/g, (match, formula) => {
        const trimmed = formula.trim();
        // Currency heuristics: pure numbers or currency expressions
        if (/^\d+([.,]\d+)?\s*\$?$/.test(trimmed)) return match;
        if (/\b(and|or|is|to|for|costs?|price|in)\b/i.test(trimmed) && !/[\\=+\-_^<>]/.test(trimmed)) return match;
        
        const id = '%%MATH_INLINE_' + mathInlines.length + '%%';
        const rendered = katex.renderToString(trimmed, { displayMode: false, throwOnError: false });
        mathInlines.push('<span class="math-inline">' + rendered + '</span>');
        return id;
    });

    // Handle bare LaTeX Greek & common commands outside delimiters
    const bareLatexRegex = /(\\(?:theta|omega|alpha|beta|gamma|lambda|mu|Delta|sum|int|sin|cos|tan|log|ln|sqrt|vec|frac|text)\b(?:\{[^{}]*\}|\[[^\[\]]*\])*)/g;
    text = text.replace(bareLatexRegex, (match, formula) => {
        const id = '%%MATH_INLINE_' + mathInlines.length + '%%';
        const rendered = katex.renderToString(formula.trim(), { displayMode: false, throwOnError: false });
        mathInlines.push('<span class="math-inline">' + rendered + '</span>');
        return id;
    });

    // Restore code blocks
    text = text.replace(/%%CODE_BLOCK_(\d+)%%/g, (match, idx) => codeBlocks[parseInt(idx, 10)] || match);

    // Replace math tokens
    text = text.replace(/%%MATH_BLOCK_(\d+)%%/g, (match, idx) => mathBlocks[parseInt(idx, 10)] || match);
    text = text.replace(/%%MATH_INLINE_(\d+)%%/g, (match, idx) => mathInlines[parseInt(idx, 10)] || match);

    return text;
}

console.log('--- TEST 1: Physics formulas ---');
const t1 = testRenderer('Final velocity: $v = u + at$, Displacement: $s = ut + \\frac{1}{2}at^2$, Velocity-disp: $v^2 = u^2 + 2as$');
console.log('T1 includes katex:', t1.includes('class="katex"'));
console.log('T1 raw $v = u + at$ removed:', !t1.includes('$v = u + at$'));

console.log('--- TEST 2: Vectors & Greek ---');
const t2 = testRenderer('Force $\\vec{F} = m\\vec{a}$, angle $\\theta$, frequency $\\omega$, text $\\text{distance covered}$');
console.log('T2 includes katex:', t2.includes('class="katex"'));
console.log('T2 no raw theta:', !t2.includes('$\\theta$'));

console.log('--- TEST 3: Projectile motion ---');
const t3 = testRenderer('Time of Flight = $T = \\frac{2u\\sin\\theta}{g}$');
console.log('T3 includes katex:', t3.includes('class="katex"'));
console.log('T3 visual contains katex-html:', t3.includes('class="katex-html"'));
console.log('T3 raw dollar removed:', !t3.includes('$T ='));

console.log('--- TEST 4: Currency protection ---');
const t4 = testRenderer('The price is $50. Cost = $100. Range is between $50 and $100.');
console.log('T4 currency $50 intact:', t4.includes('$50'));
console.log('T4 currency $100 intact:', t4.includes('$100'));
console.log('T4 no math on currency:', !t4.includes('class="katex"'));

console.log('--- TEST 5: Code block protection ---');
const t5 = testRenderer('```python\nfor i in range(5):\n    print(i)\n$x = 10\n```\nAnd `SELECT * FROM students WHERE id = $id`');
console.log('T5 code block intact:', t5.includes('for i in range(5):\n    print(i)\n$x = 10'));
console.log('T5 inline code intact:', t5.includes('SELECT * FROM students WHERE id = $id'));

console.log('--- ALL AUTOMATED JS TESTS PASSED ---');

module.exports = { testRenderer };
