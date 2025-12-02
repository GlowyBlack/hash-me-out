"use client";

import ReadingListView from "@/components/ReadingListView";

export default function ReadingListPage({ params }) {
  const { listId } = params;           

  return <ReadingListView listId={Number(listId)} />;
}
