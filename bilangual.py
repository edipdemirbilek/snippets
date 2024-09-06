import fitz  # PyMuPDF
from io import BytesIO
from PIL import Image

def merge_pdfs_side_by_side(pdf1_path, pdf2_path, output_path, dpi=150, compression_quality=75):
    # Open the two PDFs
    pdf1 = fitz.open(pdf1_path)
    pdf2 = fitz.open(pdf2_path)

    # Determine the minimum number of pages between the two PDFs
    min_pages = min(len(pdf1), len(pdf2))
    print(f"Number of pages to process: {min_pages}")

    # Create a new PDF for the output
    output_pdf = fitz.open()

    for i in range(min_pages):
        # Get the i-th page from each PDF
        page1 = pdf1.load_page(i)
        page2 = pdf2.load_page(i)

        # Get the dimensions of the pages
        width1, height1 = page1.rect.width, page1.rect.height
        width2, height2 = page2.rect.width, page2.rect.height
        print(f"Processing page {i + 1}:")
        print(f"  PDF1 - Width: {width1}, Height: {height1}")
        print(f"  PDF2 - Width: {width2}, Height: {height2}")

        # Initialize variables for scaled page dimensions
        new_width1 = width1
        new_height1 = height1
        new_width2 = width2
        new_height2 = height2

        # Determine scaling factors to match the larger page dimensions
        if width1 > width2 or height1 > height2:
            scale_x = width1 / width2
            scale_y = height1 / height2
            scale = max(scale_x, scale_y)
            new_width2 = width2 * scale
            new_height2 = height2 * scale
            print(f"  Scaling PDF2 by a factor of {scale}")
            page2_pix = page2.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        else:
            page2_pix = page2.get_pixmap(alpha=False)

        if width2 > width1 or height2 > height1:
            scale_x = width2 / width1
            scale_y = height2 / height1
            scale = max(scale_x, scale_y)
            new_width1 = width1 * scale
            new_height1 = height1 * scale
            print(f"  Scaling PDF1 by a factor of {scale}")
            page1_pix = page1.get_pixmap(matrix=fitz.Matrix(scale, scale), alpha=False)
        else:
            page1_pix = page1.get_pixmap(alpha=False)

        # Convert Pixmap to PIL Image and then to JPEG
        def pixmap_to_jpeg_bytes(pixmap, quality):
            # Convert pixmap to bytes
            img = Image.open(BytesIO(pixmap.tobytes()))
            # Save as JPEG with quality
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=quality)
            img_bytes.seek(0)
            return img_bytes

        img1_bytes = pixmap_to_jpeg_bytes(page1_pix, compression_quality)
        img2_bytes = pixmap_to_jpeg_bytes(page2_pix, compression_quality)

        # Create a new page with combined width and max height
        new_width = int(new_width1 + new_width2 + 20)  # Adding 20 units for white space
        new_height = int(max(new_height1, new_height2))
        print(f"  New page dimensions: Width: {new_width}, Height: {new_height}")
        new_page = output_pdf.new_page(width=new_width, height=new_height)

        # Insert the pages side by side
        new_page.insert_image(fitz.Rect(0, 0, new_width1, new_height1), stream=img1_bytes)
        new_page.insert_image(fitz.Rect(new_width1 + 20, 0, new_width1 + new_width2 + 20, new_height2), stream=img2_bytes)

        print(f"  Page {i + 1} processed and added to the output PDF")

    # Save the output PDF
    output_pdf.save(output_path)
    output_pdf.close()

    # Close the input PDFs
    pdf1.close()
    pdf2.close()

    print(f"PDFs merged successfully into '{output_path}'")

# Paths to the input PDFs and the output PDF
pdf1_path = 'English.pdf'
pdf2_path = 'Japanese.pdf'
output_path = 'Bilingual.pdf'

merge_pdfs_side_by_side(pdf1_path, pdf2_path, output_path)
