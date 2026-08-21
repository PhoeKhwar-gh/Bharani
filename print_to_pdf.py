"""
print_to_pdf.py
ဘရဏီ အက်ပ်အတွက် PDF Export Module
ဇာတာပုံများနှင့် အချက်အလက်များကို PDF အဖြစ် သိမ်းဆည်းခြင်း
"""

import os
from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtCore import Qt, QCoreApplication, QDir
from PyQt5.QtGui import QPainter, QColor, QFont, QPixmap, QPen  
import PyQt5.QtCore as QtCore


class BharaniPdfExporter:
    """ဘရဏီ အက်ပ်၏ PDF Export လုပ်ဆောင်ချက်များကို စီမံခန့်ခွဲသော Class"""
    
    def __init__(self, main_window):
        """
        main_window: BharaniApp instance (UI elements များကို access ရန်)
        """
        self.main_window = main_window
    
    # ==================== Helper Methods ====================
    
    def _get_pdf_header_lines(self):
        """PDF စာမျက်နှာ အပေါ်ပိုင်းအတွက် ဇာတာပါ အချက်အလက် ၇ ကြောင်း ပြန်ပေးခြင်း"""
        mw = self.main_window
        
        # === အခြေခံ အချက်အလက်များ ===
        name = mw.txtName.text().strip() or "အမည်မသိ"
        birth_date = mw.cboDate.date().toString("yyyy-MM-dd")
        birth_time = mw.cboTime.time().toString("HH:mm:ss")
        city = mw.cboCity.currentText()
        country = mw.cboCountry.currentText()
        lat = mw.txtLat.text()
        lon = mw.txtLon.text()
        
        # === ဇာတာပါ အချက်အလက်များ ===
        lagna_info = "—"
        sun_info = "—"
        moon_info = "—"
        
        if hasattr(mw, 'current_planet_data') and mw.current_planet_data:
            for p in mw.current_planet_data:
                p_name = p.get('name', '')
                sign_name = p.get('sign_name', '').strip()
                deg = p.get('deg', 0)
                min_val = p.get('min', 0)
                
                # Sign name ကို 3 လုံး အကျဉ်းချုံးခြင်း
                sign_short = sign_name[:3] if sign_name else "?"
                pos_str = f"{sign_short} {deg}°{min_val}'"
                
                if p_name == 'Lagna':
                    lagna_info = f"{sign_name.strip()} {deg}°{min_val}'"
                elif p_name == 'Sun':
                    sun_info = pos_str
                elif p_name == 'Moon':
                    moon_info = pos_str
        
        # === အာယန နှင့် ဘာဝစနစ် ===
        ayanamsa = mw.cboAyana.currentText()
        house_sys = mw.cboHouseSys.currentText()
        
        # === စာကြောင်း ၇ ကြောင်း ပြန်ပေးခြင်း ===
        return [
            f"ဇေယျတု သဗ္ဗမင်္ဂလံ, မြန်မာ သက္ကရာဇ် ၁၃၈၈ ခုနှစ်၊  အမည် - {name}",
            f"မွေးနေ့ - {birth_date}  |  မွေးချိန် - {birth_time}",
            f"မွေးမြို့ - {city}, {country}",
            f"လတ္တီတွဒ် - {lat}  |  လောင်ဂျီတွဒ် - {lon}",
            f"လဂ်နာ - {lagna_info}",
            f"နေတည်ရာ - {sun_info}  |  လတည်ရာ - {moon_info}",
            f"အာယန - {ayanamsa}  |  ဘာဝစနစ် - {house_sys}"
        ]
    
    def _grab_charts_pixmap(self):
        """ဇာတာပုံ widget မှ pixmap ကို ဖမ်းယူခြင်း (Full Size)"""
        mw = self.main_window
        widget = mw.charts_container
        widget.ensurePolished()
        
        # ✅ ScrollArea အတွင်းမှာ ရှိနေပေမယ့် Full Size ပုံရိပ်ယူနိုင်ရန်
        original_size = widget.size()
        widget.resize(widget.sizeHint())
        widget.adjustSize()
        QCoreApplication.processEvents()
        
        pixmap = widget.grab()
        
        # ✅ မူလအရွယ်အစားသို့ ပြန်ထားခြင်း
        widget.resize(original_size)
        
        if pixmap.isNull():
            raise Exception("ဇာတာပုံ widget ကို ဖမ်းယူ၍ မရပါ။")
        
        return pixmap
    
    def _draw_pdf_header(self, painter, page_x, page_y, page_w, dpi, info_lines):
        """PDF စာမျက်နှာ အပေါ်ပိုင်းတွင် အချက်အလက်များ ရေးသားခြင်း"""
        # ✅ Painter state ကို save လုပ်ခြင်း
        painter.save()
        
        # ✅ Font သတ်မှတ်ခြင်း
        header_font = QFont("Pyidaungsu", 11)
        painter.setFont(header_font)
        
        # ✅ ✅ ✅ အဓိက ပြင်ဆင်ချက် - QPen ြင့် အနက်ရောင်ကို explicitly သတ်မှတ်ခြင်း
        black_pen = QPen(QColor(0, 0, 0))  # RGB: 0,0,0 = အနက်ရောင်
        black_pen.setWidth(1)
        painter.setPen(black_pen)
        
        line_height = int(dpi * 0.25)  # တစ်ကြောင်းလျှင် 0.25 inch
        text_y = page_y
        
        for line in info_lines:
            painter.drawText(
                page_x, text_y, page_w, line_height,
                Qt.AlignLeft | Qt.AlignVCenter, line
            )
            text_y += line_height
        
        # Header အတွက် စုစုပေါင်း အမြင့် ပြန်ပေးခြင်း
        header_total_height = len(info_lines) * line_height + int(dpi * 0.1)
        
        # ✅ Painter state ကို restore လုပ်ခြင်း
        painter.restore()
            
        return header_total_height
    
    def _draw_pdf_page(self, painter, paper_rect, page_x, page_y, page_w, page_h,
                       scaled_pixmap, y_offset, header_height=0):
        """PDF စာမျက်နှာ တစ်ခုကို ရေးဆွဲခြင်း"""
        # Chart ကို ရေးဆွဲခြင်း
        segment_h = int(min(page_h - header_height, scaled_pixmap.height() - y_offset))
        
        if segment_h <= 0:
            return 0, False  # segment_h, continue_drawing
        
        # ✅ Left margin 0.35 inch, Center alignment
        x = page_x + max(0, (page_w - scaled_pixmap.width()) // 2)
        
        # ✅ Top margin 0.35 inch + header height
        painter.drawPixmap(
            x,
            page_y + header_height,
            scaled_pixmap,
            0,
            y_offset,
            scaled_pixmap.width(),
            segment_h
        )
        
        return segment_h, True  # segment_h, continue_drawing
    
    # ==================== Main Export Method ====================
    
    def export_charts_to_pdf(self):
        """တွက်ချက်ပြီး ဇာတာပုံများကို PDF အဖြစ် သိမ်းဆည်းခြင်း
        A4, Full Page, Margin 0.35 inch around
        """
        mw = self.main_window
        
        if not getattr(mw, "current_planet_data", None):
            QMessageBox.warning(
                mw, "သတိပေးချက်",
                "ကျေးဇူးပြု၍ ဦးစွာ ဇာတာကို တွက်ချက်ပေးပါ။"
            )
            return
        
        # === File Path Selection ===
        default_name = mw.txtName.text().strip() or "Zarta"
        settings = QtCore.QSettings("MyCompany", "BharaniApp")
        last_dir = settings.value("lastPdfExportDir", QDir.homePath())
        default_path = os.path.join(last_dir, f"{default_name}.pdf")
        
        file_path, _ = QFileDialog.getSaveFileName(
            mw, "PDF ဖိုင် သိမ်းရန် နေရာ ရွေးပါ",
            default_path, "PDF Files (*.pdf)"
        )
        
        if not file_path:
            mw.statusbar.showMessage("PDF သိမ်းဆည်းခြင်း မလုပ်ပါ")
            return
        
        if not file_path.lower().endswith(".pdf"):
            file_path += ".pdf"
        
        settings.setValue("lastPdfExportDir", os.path.dirname(file_path))
        
        # === PDF Generation ===
        painter = QPainter()
        painter_started = False
        error_message = None
        
        try:
            # Printer Setup
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(file_path)
            printer.setPageSize(QPrinter.A4)
            printer.setResolution(300)  # ✅ 300 DPI (ပိုကြည်လင်)
            printer.setFullPage(True)
            
            # ✅ Widget Grab
            pixmap = self._grab_charts_pixmap()
            
            if not painter.begin(printer):
                raise Exception("PDF writer ကို စတင်၍ မရပါ။")
            
            painter_started = True
            
            # Page Dimensions
            dpi = printer.resolution()
            margin_inch = 0.35
            margin_px = int(margin_inch * dpi)
            paper_rect = printer.paperRect(QPrinter.DevicePixel)
            page_x = margin_px
            page_y = margin_px
            page_w = int(paper_rect.width()) - 2 * margin_px
            page_h = int(paper_rect.height()) - 2 * margin_px
            
            if page_w <= 0 or page_h <= 0:
                raise Exception("PDF စာမျက်နှာ အရွယ်အစား မမှန်ပါ။")
            
            # ✅ Header Info
            info_lines = self._get_pdf_header_lines()
            
            # Scale pixmap to page width
            scaled = pixmap.scaledToWidth(page_w, Qt.SmoothTransformation)
            
            if scaled.isNull() or scaled.height() <= 0:
                raise Exception("PDF အတွက် ပုံဖမ်းယူမှု မအောင်မြင်ပါ။")
            
            # === Pagination Loop ===
            y = 0
            first_page = True
            
            while y < scaled.height():
                if not first_page:
                    printer.newPage()

                # Header မရေးမီ နောက်ခံကို ဖြည့်ရန်၊ header မပျောက်စေရန်
                painter.fillRect(paper_rect, QColor(Qt.white))
                
                # ✅ First page: Draw header
                header_height = 0
                if first_page:
                    header_height = self._draw_pdf_header(
                        painter, page_x, page_y, page_w, dpi, info_lines
                    )
                    first_page = False
                
                # ✅ Draw page content
                segment_h, continue_drawing = self._draw_pdf_page(
                    painter, paper_rect, page_x, page_y, page_w, page_h,
                    scaled, y, header_height
                )
                
                if not continue_drawing:
                    break
                
                y += segment_h
        
        except Exception as e:
            error_message = str(e)
            import traceback
            traceback.print_exc()
        
        finally:
            if painter_started:
                painter.end()
        
        # === Result Message ===
        if error_message:
            QMessageBox.critical(
                mw, "အမှား",
                f"PDF သိမ်းဆည်းရာတွင် အမှားရှိနေပါသည်:\n{error_message}"
            )
        else:
            mw.statusbar.showMessage(f"✅ PDF သိမ်းပြီး: {file_path}")
            QMessageBox.information(
                mw, "အောင်မြင်ပါသည်",
                f"PDF ဖိုင်ကို အောင်မြင်စွာ သိမ်းဆည်းပြီးပါပြီ။\n{file_path}"
            )


# ==================== Convenience Function ====================

def export_charts_to_pdf(main_window):
    """
    Convenience function - BharaniPdfExporter ကို အသုံးပြုပြီး PDF export လုပ်ခြင်း
    main_window: BharaniApp instance
    """
    exporter = BharaniPdfExporter(main_window)
    exporter.export_charts_to_pdf()