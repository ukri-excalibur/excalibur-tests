for compiler in $(cat compilers)
do (
module load $compiler &> /dev/null &&
for mpi in $(cat mpis);
do (
module load $mpi &> /dev/null && echo $compiler $mpi 
)
done
)
done
