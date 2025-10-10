type StartupViewProps = {
  title?: string;
};

export default function StartupView({ title = "🚀 Startup View Page" }: StartupViewProps) {
  return <h1>{title}</h1>;
}
