/**
 * Digital Canteen Token System - Zero-Dependency SVG Chart Renderer
 */

class SVGCharts {
    static renderLineChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const width = options.width || container.clientWidth || 500;
        const height = options.height || 220;
        const padding = 35;

        if (!data || data.length === 0) {
            container.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-muted)">No chart data available</div>`;
            return;
        }

        const maxVal = Math.max(...data.map(d => d.value), 10);
        const xStep = (width - padding * 2) / (data.length - 1 || 1);

        let points = [];
        let dots = '';
        let labels = '';

        data.forEach((d, i) => {
            const x = padding + (i * xStep);
            const y = height - padding - ((d.value / maxVal) * (height - padding * 2));
            points.push(`${x},${y}`);

            dots += `<circle cx="${x}" cy="${y}" r="4" fill="#10b981" stroke="#ffffff" stroke-width="2">
                <title>${d.label}: ${d.value} orders</title>
            </circle>`;

            if (i % Math.ceil(data.length / 6) === 0 || i === data.length - 1) {
                labels += `<text x="${x}" y="${height - 10}" text-anchor="middle" font-size="11" fill="var(--text-muted)">${d.label}</text>`;
            }
        });

        const polyline = `<polyline fill="none" stroke="#10b981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" points="${points.join(' ')}" />`;
        
        // Gradient area
        const areaPoints = `${padding},${height - padding} ${points.join(' ')} ${padding + (data.length - 1) * xStep},${height - padding}`;
        const areaPolygon = `<polygon fill="url(#lineGrad)" opacity="0.25" points="${areaPoints}" />`;

        container.innerHTML = `
            <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}" style="overflow:visible;">
                <defs>
                    <linearGradient id="lineGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#10b981" />
                        <stop offset="100%" stop-color="#10b981" stop-opacity="0" />
                    </linearGradient>
                </defs>
                <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="var(--border)" stroke-width="1" />
                ${areaPolygon}
                ${polyline}
                ${dots}
                ${labels}
            </svg>
        `;
    }

    static renderBarChart(containerId, data, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const width = options.width || container.clientWidth || 500;
        const height = options.height || 220;
        const padding = 35;

        if (!data || data.length === 0) {
            container.innerHTML = `<div style="text-align:center;padding:2rem;color:var(--text-muted)">No forecast data available</div>`;
            return;
        }

        const maxVal = Math.max(...data.map(d => d.value), 20);
        const barWidth = Math.min(32, (width - padding * 2) / (data.length * 1.5));
        const totalSlot = (width - padding * 2) / data.length;

        let bars = '';
        let labels = '';

        data.forEach((d, i) => {
            const x = padding + (i * totalSlot) + (totalSlot - barWidth) / 2;
            const barHeight = (d.value / maxVal) * (height - padding * 2);
            const y = height - padding - barHeight;

            bars += `
                <rect x="${x}" y="${y}" width="${barWidth}" height="${barHeight}" rx="4" fill="url(#barGrad)">
                    <title>${d.label}: ${d.value} portions</title>
                </rect>
                <text x="${x + barWidth / 2}" y="${y - 6}" text-anchor="middle" font-size="11" font-weight="bold" fill="var(--text-primary)">${d.value}</text>
            `;

            labels += `<text x="${x + barWidth / 2}" y="${height - 12}" text-anchor="middle" font-size="10" fill="var(--text-muted)">${d.label.slice(0, 10)}</text>`;
        });

        container.innerHTML = `
            <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}">
                <defs>
                    <linearGradient id="barGrad" x1="0%" y1="0%" x2="0%" y2="100%">
                        <stop offset="0%" stop-color="#6366f1" />
                        <stop offset="100%" stop-color="#4f46e5" />
                    </linearGradient>
                </defs>
                <line x1="${padding}" y1="${height - padding}" x2="${width - padding}" y2="${height - padding}" stroke="var(--border)" stroke-width="1" />
                ${bars}
                ${labels}
            </svg>
        `;
    }
}

window.SVGCharts = SVGCharts;
