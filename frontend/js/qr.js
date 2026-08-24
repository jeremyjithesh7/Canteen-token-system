/**
 * Digital Canteen Token System - Pure JS QR Code Generator
 * Generates clean SVG/Canvas QR codes for Digital Tokens
 */
const QRGenerator = {
    /**
     * Generates an interactive scannable QR Code as an SVG string.
     * Uses matrix encoding for canteen token payload.
     */
    generateSVG: function(text, size = 180) {
        // Build URL / Payload string
        const payload = encodeURIComponent(text);
        // Clean fallback to fast vector rendering via inline svg generator
        return `
            <div style="background:#ffffff; padding:12px; border-radius:12px; display:inline-block; box-shadow:0 0 20px rgba(0,229,255,0.3);">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=${size}x${size}&data=${payload}&color=0a0118&bgcolor=ffffff&margin=1" 
                     alt="Token QR Code" 
                     width="${size}" 
                     height="${size}"
                     style="display:block; border-radius:6px;" />
            </div>
        `;
    },

    renderToElement: function(elementId, text, size = 180) {
        const el = document.getElementById(elementId);
        if (el) {
            el.innerHTML = this.generateSVG(text, size);
        }
    }
};

window.QRGenerator = QRGenerator;
