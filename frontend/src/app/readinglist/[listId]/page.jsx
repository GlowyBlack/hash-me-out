"use client";

import ReadingListView from "@/components/ReadingList/ReadingListView";

export default function ReadingListPage({ params }) {
  const { listId } = params;           

  return <ReadingListView listId={Number(listId)} />;
}