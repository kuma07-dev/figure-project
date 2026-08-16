import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const deck = await PresentationFile.importPptx(
  await FileBlob.load("C:/Users/student/Desktop/ichiban-arbitrage-system/presentation/ichiban-arbitrage-midterm.pptx"),
);
const snapshot = await deck.inspect({ kind: "textbox", maxChars: 120000 });
for (const line of snapshot.ndjson.split("\n")) {
  if (!line.trim()) continue;
  const item = JSON.parse(line);
  console.log(JSON.stringify({ slide: item.slide, id: item.id, text: item.textPreview }));
}
