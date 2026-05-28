import MatchingGame from "@/app/games/matching/MatchingGame";

export const metadata = {
  title: "Memory Game",
  description: "A simple memory card matching game",
};

export default function Page() {
  return <MatchingGame />;
}
