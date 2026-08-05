interface AvatarProps {
  src?: string;
  name: string;
  size?: 'sm' | 'md' | 'lg';
  online?: boolean;
  className?: string;
}

const sizeMap = {
  sm: 'w-8 h-8 text-xs',
  md: 'w-10 h-10 text-sm',
  lg: 'w-12 h-12 text-base',
};

const dotSizeMap = {
  sm: 'w-2.5 h-2.5 border-[1.5px]',
  md: 'w-3 h-3 border-2',
  lg: 'w-3.5 h-3.5 border-2',
};

const colors = [
  'bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-pink-500',
  'bg-yellow-500', 'bg-red-500', 'bg-indigo-500', 'bg-teal-500',
];

function getColorFromName(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function Avatar({ src, name, size = 'md', online, className = '' }: AvatarProps) {
  return (
    <div className={`relative flex-shrink-0 ${className}`}>
      {src ? (
        <img
          src={src}
          alt={name}
          className={`${sizeMap[size]} rounded-full object-cover`}
        />
      ) : (
        <div
          className={`${sizeMap[size]} ${getColorFromName(name)} rounded-full flex items-center justify-center text-white font-semibold`}
        >
          {getInitials(name)}
        </div>
      )}
      {online && (
        <div
          className={`absolute bottom-0 right-0 ${dotSizeMap[size]} bg-online rounded-full border-white dark:border-messenger-dark-bg online-pulse`}
        />
      )}
    </div>
  );
}
