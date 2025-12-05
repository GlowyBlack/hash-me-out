"use client";

import { useSearchParams } from "next/navigation";
import ReadingListView from "@/components/ReadingList/ReadingListView";

export default function PublicReadingListPage({ params }) {
  const { listId } = params;
  const searchParams = useSearchParams();
  const owner = searchParams.get("owner");

  return (
    <ReadingListView
      listId={Number(listId)}
      readOnly={true}
      ownerId={owner ? Number(owner) : null}
    />
  );
}
