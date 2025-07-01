import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

export const exportToPDF = async () => {
  try {
    console.log('PDF export started...');
    
    // Try to find which content element exists on the current page
    const yearlyElement = document.getElementById('yearly-analysis-content');
    const monthlyElement = document.getElementById('monthly-analysis-content');
    const postElement = document.getElementById('post-analysis-content');
    
    let currentElement: HTMLElement | null = null;
    let pageTitle = 'Instagram Analysis';
    
    if (yearlyElement) {
      currentElement = yearlyElement;
      pageTitle = 'Yearly Analysis';
    } else if (monthlyElement) {
      currentElement = monthlyElement;
      pageTitle = 'Monthly Analysis';
    } else if (postElement) {
      currentElement = postElement;
      pageTitle = 'Post Analysis';
    }
    
    if (!currentElement) {
      throw new Error('No analysis content found on current page');
    }

    // Create temporary style to override OKLCH colors for PDF export
    const tempStyle = document.createElement('style');
    tempStyle.textContent = `
      /* Override OKLCH colors with hex equivalents for PDF export */
      * {
        color: rgb(64, 71, 73) !important;
        border-color: rgb(245, 245, 245) !important;
        background-color: inherit !important;
      }
      .rdp-button {
        background-color: #ffffff !important;
        color: #404749 !important;
        border-color: #f5f5f5 !important;
      }
      .rdp-day_selected {
        background-color: #f3a522 !important;
        color: #322c2c !important;
      }
      [data-state="active"] {
        background-color: #f3a522 !important;
        color: #322c2c !important;
      }
      .bg-primary {
        background-color: #f3a522 !important;
      }
      .text-primary {
        color: #f3a522 !important;
      }
      .border-primary {
        border-color: #f3a522 !important;
      }
    `;
    document.head.appendChild(tempStyle);

    // Create PDF document
    const pdf = new jsPDF('l', 'mm', 'a4'); // landscape orientation
    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();

    try {
      // Capture the current page content
      const canvas = await html2canvas(currentElement, {
        scale: 2,
        height: currentElement.scrollHeight,
        width: currentElement.scrollWidth,
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff'
      });

      const imgData = canvas.toDataURL('image/png');
      
      // Calculate dimensions to fit the page
      const imgAspectRatio = canvas.width / canvas.height;
      const pdfAspectRatio = pdfWidth / pdfHeight;
      
      let imgWidth, imgHeight;
      if (imgAspectRatio > pdfAspectRatio) {
        // Image is wider relative to PDF
        imgWidth = pdfWidth;
        imgHeight = pdfWidth / imgAspectRatio;
      } else {
        // Image is taller relative to PDF
        imgHeight = pdfHeight;
        imgWidth = pdfHeight * imgAspectRatio;
      }
      
      // Center the image on the page
      const x = (pdfWidth - imgWidth) / 2;
      const y = (pdfHeight - imgHeight) / 2;

      pdf.addImage(imgData, 'PNG', x, y, imgWidth, imgHeight);

      // Save the PDF
      const currentDate = new Date().toISOString().split('T')[0];
      const fileName = `instagram-${pageTitle.toLowerCase().replace(' ', '-')}-${currentDate}.pdf`;
      pdf.save(fileName);
      
      console.log(`PDF export completed successfully: ${fileName}`);
      return true;

    } finally {
      // Remove the temporary style
      document.head.removeChild(tempStyle);
    }

  } catch (error) {
    console.error('PDF export failed:', error);
    alert('PDFエクスポートに失敗しました。');
    return false;
  }
};