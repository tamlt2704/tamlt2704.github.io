import Image from "next/image";
import { HelloComponent } from '@/components/HellloComponent';

export default function Home() {
  return (
    <div>
      <Image src={'/matrix.jpg'} width={400} height={400} alt="matrix" />
      <HelloComponent />
    </div>
  );
}
