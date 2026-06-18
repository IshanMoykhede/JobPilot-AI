/**
 * Client-side PDF structured text extractor using Mozilla PDF.js.
 * Merges broken word fragments, clusters text into visual rows,
 * and groups columns by horizontal proximity.
 */

export async function extractStructuredText(pdf) {
  const pages = [];

  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
    let pageText = "";
    const page = await pdf.getPage(pageNum);
    const content = await page.getTextContent();
    const viewport = page.getViewport({ scale: 1 });

    // Collect all items — preserve single chars (grades, scores)
    let items = content.items
      .map((item) => ({
        str: item.str.trim(),
        x: item.transform[4],
        y: viewport.height - item.transform[5],
        width: Math.abs(item.width) || 0,
        centerX: item.transform[4] + Math.abs(item.width || 0) / 2,
      }))
      .filter((item) => item.str.length > 0);

    // Sort top→bottom, left→right with 14px y-tolerance
    items.sort((a, b) => {
      if (Math.abs(a.y - b.y) > 14) return a.y - b.y;
      return a.x - b.x;
    });

    // ── STEP 1: Merge word-fragments that pdfjs splits mid-word ──
    const merged = [];
    for (const item of items) {
      const prev = merged[merged.length - 1];
      if (
        prev &&
        Math.abs(item.y - prev.y) <= 14 &&
        item.x <= prev.x + prev.width + 4 &&
        !prev.str.endsWith(" ") &&
        !item.str.startsWith(" ")
      ) {
        prev.str = prev.str + item.str;
        prev.width = item.x + item.width - prev.x;
        prev.centerX = prev.x + prev.width / 2;
      } else {
        merged.push({ ...item });
      }
    }
    items = merged;

    // ── STEP 2: Group into visual rows ──
    const rows = [];
    let currentRow = [];
    let lastY = null;
    for (const item of items) {
      if (lastY !== null && Math.abs(item.y - lastY) > 14) {
        if (currentRow.length > 0) rows.push(currentRow);
        currentRow = [];
      }
      currentRow.push(item);
      lastY = item.y;
    }
    if (currentRow.length > 0) rows.push(currentRow);

    // ── Detect columns using centerX clustering (50px gap) ──
    const allCenterX = items.map((i) => i.centerX).sort((a, b) => a - b);
    const columns = buildColumns(allCenterX, 50);

    // ── Always render as plain lines — no markdown tables ever ──
    for (const row of rows) {
      const cells = assignToCols(row, columns);
      const filled = cells.filter((c) => c.trim().length > 0);
      if (filled.length === 0) continue;
      pageText += filled.join("  ").trim() + "\n";
    }

    pages.push({ text: pageText.trim(), page: pageNum });
  }

  return pages;
}

function buildColumns(sortedXValues, gapThreshold = 50) {
  if (sortedXValues.length === 0) return [];
  const columns = [];
  let clusterVals = [sortedXValues[0]];

  for (let i = 1; i < sortedXValues.length; i++) {
    if (sortedXValues[i] - sortedXValues[i - 1] > gapThreshold) {
      const center =
        clusterVals.reduce((s, v) => s + v, 0) / clusterVals.length;
      columns.push({ center });
      clusterVals = [];
    }
    clusterVals.push(sortedXValues[i]);
  }
  const center = clusterVals.reduce((s, v) => s + v, 0) / clusterVals.length;
  columns.push({ center });
  return columns;
}

function assignToCols(row, columns) {
  const rowCells = new Array(columns.length).fill("");
  for (const cell of row) {
    let bestCol = 0;
    let minDist = Infinity;
    for (let i = 0; i < columns.length; i++) {
      const dist = Math.abs(cell.centerX - columns[i].center);
      if (dist < minDist) {
        minDist = dist;
        bestCol = i;
      }
    }
    rowCells[bestCol] = (rowCells[bestCol] + " " + cell.str).trim();
  }
  return rowCells;
}
